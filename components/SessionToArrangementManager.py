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
        self.song.unfocus_all_tracks()
        self.song.normal_tempo = self.song.tempo
        self.song.tempo = 999
        self.parent.navigationManager.show_arrangement()

        seq = Sequence()
        seq.add(self.system.clear_arrangement)
        seq.add(wait=20)
        seq.add(self.parent.navigationManager.show_session)
        seq.add(self.song.reset)
        seq.add(partial(setattr, self.song, "record_mode", True))
        seq.add(wait=1)

        # make recording start at 1.1.1
        seq.add(self._start_recording_on_beginning)
        seq.add(complete_on=self.song.session_end_listener, no_timeout=True)
        seq.add(self.song.reset)
        seq.add(self.song.activate_arrangement)
        seq.add(partial(setattr, SessionToArrangementManager, "IS_BOUNCING", False))
        return seq.done()

    def _start_recording_on_beginning(self):
        # type: () -> None
        self.song.record_mode = True
        loop_start = self.song.loop_start
        loop_length = self.song.loop_length
        self.song.loop_start = 0
        self.song.loop_length = self.song.signature_numerator
        self.song.loop = True
        self.song.play_session(from_beginning=True)
        seq = Sequence()
        seq.add(complete_on=self.song.scenes[0].is_playing_listener, no_timeout=True)
        seq.add(partial(self._restore_arrangement_loop, loop_start, loop_length))
        seq.done()

    def _restore_arrangement_loop(self, loop_start, loop_length):
        # type: (float, float) -> None
        self.song.loop_start = loop_start
        self.song.loop_start = loop_length
        self.song.loop = False
