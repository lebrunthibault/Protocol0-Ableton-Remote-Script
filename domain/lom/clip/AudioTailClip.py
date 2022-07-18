from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class AudioTailClip(AudioClip):
    def post_record(self, bar_length):
        # type: (int) -> None
        super(AudioTailClip, self).post_record(bar_length)
        if bar_length == 0:
            return None

        self.clip_name.update("")

        clip_end = bar_length * SongFacade.signature_numerator()
        if clip_end == self.loop.end:
            self.delete()
        else:
            self.loop.looping = False
            self.loop.start = clip_end
            self.muted = True

    def play_and_mute(self):
        # type: () -> Sequence
        self.muted = False
        seq = Sequence()

        seq.defer()  # wait for unmute
        seq.log("play and mute")
        seq.add(self.fire)
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)  # wait for the clip
        # start
        seq.wait_bars(self.loop.bar_length)
        seq.wait(5)
        seq.add(self._mute_if_stopped)

        return seq.done()

    def _mute_if_stopped(self):
        # type: () -> None
        if not self.is_playing:
            self.muted = True
