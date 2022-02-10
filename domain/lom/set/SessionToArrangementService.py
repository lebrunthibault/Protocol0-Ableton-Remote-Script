from functools import partial

from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.System import System
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.domain.lom.scene.Scene import Scene

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class SessionToArrangementService(object):
    def __init__(self, song):
        # type: (Song) -> None
        self._song = song
        self._tempo = self._song.tempo
        self._is_bouncing = False

    def bounce_session_to_arrangement(self):
        # type: () -> Optional[Sequence]
        self._prepare_for_bounce()

        if self._is_bouncing:
            self._finish()
            Scheduler.defer(ApplicationView.show_session)
            return None

        Scene.LOOPING_SCENE = None
        self._is_bouncing = True
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

    def _prepare_for_bounce(self):
        # type: () -> None
        """ Stop the song when the last scene finishes """
        last_scene = SongFacade.scenes()[-1]
        seq = Sequence()
        seq.add(complete_on=last_scene.is_triggered_listener)
        seq.add(wait_for_event=BarEndingEvent)
        seq.add(self._song.stop_all_clips)
        seq.done()

    def _finish(self):
        # type: () -> None
        self._song.reset()
        self._song.record_mode = False
        self._song.tempo = self._tempo
        self._is_bouncing = False
