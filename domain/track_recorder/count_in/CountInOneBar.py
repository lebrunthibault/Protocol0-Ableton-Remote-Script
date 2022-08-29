from functools import partial

from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class CountInOneBar(CountInInterface):
    def launch(self):
        # type: () -> Sequence
        self._playback_component.stop()
        self._playback_component.metronome = True
        # solo for count in
        track_solo = self._track.solo
        self._track.solo = True
        self._playback_component.start_playing()
        seq = Sequence()
        seq.wait_for_event(LastBeatPassedEvent, continue_on_song_stop=True)
        seq.add(partial(setattr, self._track, "solo", track_solo))
        seq.add(self._stop_count_in)
        return seq.done()

    def _stop_count_in(self):
        # type: () -> None
        if (
            len([clip for clip in SongFacade.selected_scene().clips if not clip.muted]) >= 1
            and not self._track.solo
        ):
            self._playback_component.metronome = False
