from functools import partial

from typing import Optional, TYPE_CHECKING

from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.System import System
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.AccessSong import AccessSong

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


class SessionToArrangementManager(AccessSong):
    IS_BOUNCING = False
    LAST_SCENE_FIRED = None   # type: Optional[Scene]

    def bounce_session_to_arrangement(self):
        # type: () -> Optional[Sequence]
        if SessionToArrangementManager.IS_BOUNCING:
            self._song.session_end_listener()
            Scheduler.defer(ApplicationView.show_session)
            return None

        from protocol0.domain.lom.scene.Scene import Scene

        Scene.LOOPING_SCENE = None
        SessionToArrangementManager.IS_BOUNCING = True
        SessionToArrangementManager.LAST_SCENE_FIRED = None
        self._song.unfocus_all_tracks()
        self._song.normal_tempo = self._song.tempo
        self._song.tempo = 999
        ApplicationView.show_arrangement()

        seq = Sequence()
        seq.add(System.get_instance().clear_arrangement)
        seq.add(wait=20)
        seq.add(ApplicationView.show_session)
        seq.add(self._song.reset)
        # make recording start at 1.1.1
        seq.add(self._song.scenes[0].pre_fire)
        seq.add(partial(setattr, self._song, "record_mode", True))
        seq.add(complete_on=self._song.session_end_listener, no_timeout=True)
        seq.add(self._song.reset)
        seq.add(ApplicationView.show_arrangement)
        seq.add(partial(setattr, self._song, "back_to_arranger", False))
        seq.add(partial(setattr, SessionToArrangementManager, "IS_BOUNCING", False))
        seq.add(partial(setattr, SessionToArrangementManager, "LAST_SCENE_FIRED", None))
        return seq.done()
