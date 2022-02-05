from functools import partial

from typing import Optional, TYPE_CHECKING

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.ApplicationView import ApplicationView
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.infra.System import System

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


class SessionToArrangementManager(AbstractControlSurfaceComponent):
    IS_BOUNCING = False
    LAST_SCENE_FIRED = None   # type: Optional[Scene]

    def bounce_session_to_arrangement(self):
        # type: () -> Optional[Sequence]
        if SessionToArrangementManager.IS_BOUNCING:
            self.song.session_end_listener()
            self.parent.defer(ApplicationView.show_session)
            return None

        from protocol0.domain.lom.scene.Scene import Scene

        Scene.LOOPING_SCENE = None
        SessionToArrangementManager.IS_BOUNCING = True
        SessionToArrangementManager.LAST_SCENE_FIRED = None
        self.song.unfocus_all_tracks()
        self.song.normal_tempo = self.song.tempo
        self.song.tempo = 999
        ApplicationView.show_arrangement()

        seq = Sequence()
        seq.add(System.get_instance().clear_arrangement)
        seq.add(wait=20)
        seq.add(ApplicationView.show_session)
        seq.add(self.song.reset)
        # make recording start at 1.1.1
        seq.add(self.song.scenes[0].pre_fire)
        seq.add(partial(setattr, self.song, "record_mode", True))
        seq.add(complete_on=self.song.session_end_listener, no_timeout=True)
        seq.add(self.song.reset)
        seq.add(ApplicationView.show_arrangement)
        seq.add(partial(setattr, self._song, "back_to_arranger", False))
        seq.add(partial(setattr, SessionToArrangementManager, "IS_BOUNCING", False))
        seq.add(partial(setattr, SessionToArrangementManager, "LAST_SCENE_FIRED", None))
        return seq.done()
