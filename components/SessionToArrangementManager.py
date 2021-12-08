from functools import partial

from typing import Optional

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.sequence.Sequence import Sequence


class SessionToArrangementManager(AbstractControlSurfaceComponent):
    IS_BOUNCING = False

    def bounce_session_to_arrangement(self):
        # type: () -> Optional[Sequence]
        if SessionToArrangementManager.IS_BOUNCING:
            self.song.session_end_listener()
            self.parent.defer(self.parent.navigationManager.show_session)
            return None

        SessionToArrangementManager.IS_BOUNCING = True
        tempo = self.song.tempo
        self.song.unfocus_all_tracks()
        self.song.tempo = 999
        self.parent.sceneBeatScheduler.clear()

        self.parent.navigationManager.show_arrangement()

        seq = Sequence()
        seq.add(self.system.clear_arrangement)
        seq.add(wait=20)
        seq.add(self.parent.navigationManager.show_session)
        seq.add(self.song.reset)
        seq.add(partial(setattr, self.song, "record_mode", True))
        seq.add(partial(self.song._play_session, from_beginning=True), complete_on=self.song.session_end_listener,
                no_timeout=True)
        seq.add(partial(setattr, self.song, "record_mode", False))
        seq.add(self.song.reset)
        seq.add(partial(setattr, self.song, "tempo", tempo))
        seq.add(self.song.activate_arrangement)
        seq.add(partial(setattr, SessionToArrangementManager, "IS_BOUNCING", False))
        return seq.done()
