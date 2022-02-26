from functools import partial

from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class CountInOneBar(CountInInterface):
    def launch(self):
        # type: () -> Sequence
        self._song.metronome = True
        self._song.stop_playing()
        self._song.stop_all_clips(quantized=False)  # stopping previous scene clips
        # solo for count in
        self.track.solo = True
        self._song.is_playing = True
        seq = Sequence()
        seq.wait_for_event(LastBeatPassedEvent)
        seq.add(partial(setattr, self.track, "solo", False))
        seq.add(self._stop_count_in)
        return seq.done()

    def _stop_count_in(self):
        # type: () -> None
        if len([clip for clip in SongFacade.selected_scene().clips if not clip.muted]) >= 1:
            self._song.metronome = False
