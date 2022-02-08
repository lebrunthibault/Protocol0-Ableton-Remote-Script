from functools import partial

from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.System import System
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song
    from protocol0.domain.lom.scene.Scene import Scene


class SessionToArrangementManager(object):
    IS_BOUNCING = False
    LAST_SCENE_FIRED = None   # type: Optional[Scene]

    def __init__(self, song):
        # type: (Song) -> None
        self._song = song
        self._tempo = self._song.tempo

    def bounce_session_to_arrangement(self):
        # type: () -> Optional[Sequence]
        if SessionToArrangementManager.IS_BOUNCING:
            self._finish()
            Scheduler.defer(ApplicationView.show_session)
            return None

        from protocol0.domain.lom.scene.Scene import Scene

        Scene.LOOPING_SCENE = None
        SessionToArrangementManager.IS_BOUNCING = True
        SessionToArrangementManager.LAST_SCENE_FIRED = None
        self._song.unfocus_all_tracks()
        self._tempo = self._song.tempo
        self._song.tempo = 999
        ApplicationView.show_arrangement()

        seq = Sequence()
        seq.add(System.client().clear_arrangement)
        seq.add(wait=20)
        seq.add(ApplicationView.show_session)
        seq.add(self._song.reset)
        # make recording start at 1.1.1
        seq.add(SongFacade.scenes()[0].pre_fire)
        seq.add(partial(setattr, self._song, "record_mode", True))
        seq.add(wait_for_event=SongStoppedEvent)
        seq.add(self._finish)
        seq.add(ApplicationView.show_arrangement)
        return seq.done()

    def _finish(self):
        # type: () -> None
        self._song.reset()
        self._song.record_mode = False
        self._song.tempo = self._tempo
        SessionToArrangementManager.IS_BOUNCING = False
        SessionToArrangementManager.LAST_SCENE_FIRED = None
