from functools import partial

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class AudioTailClip(AudioClip):
    def post_record(self, bar_length):
        # type: (int) -> None
        super(AudioTailClip, self).post_record(bar_length)
        if bar_length == 0:
            return None

        self.clip_name.update(base_name="")

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
        seq.add(self.fire)
        seq.wait_beats(1)
        seq.wait_bars(self.loop.bar_length)
        seq.wait(10)
        seq.add(partial(setattr, self, "muted", True))
        return seq.done()
