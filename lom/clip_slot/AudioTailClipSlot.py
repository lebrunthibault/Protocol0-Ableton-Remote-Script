from functools import partial

from typing import Any, Optional

from protocol0.lom.clip.AudioTailClip import AudioTailClip
from protocol0.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot


class AudioTailClipSlot(AudioClipSlot):
    __subject_events__ = ("is_silent",)

    CLIP_CLASS = AudioTailClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioTailClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioTailClip]
        self._is_silent_listener.subject = self

    @p0_subject_slot("beat_changed")
    def _beat_changed_listener(self):
        # type: () -> None
        if self.track.output_meter_left < 0.1:
            # noinspection PyUnresolvedReferences
            self.notify_is_silent()

    @p0_subject_slot("is_silent")
    def _is_silent_listener(self):
        # type: () -> None
        pass

    def wait_for_silence(self, bar_length):
        # type: (int) -> Sequence
        seq = Sequence()
        seq.add(wait_beats=(bar_length * self.song.signature_numerator) - 1)
        seq.add(partial(setattr, self._beat_changed_listener, "subject", self.parent.beatScheduler))
        seq.add(complete_on=self._is_silent_listener, no_timeout=True)
        seq.add(partial(setattr, self._beat_changed_listener, "subject", None))
        return seq.done()

    def record(self, bar_length):
        # type: (int) -> Sequence
        seq = Sequence()
        seq.add(partial(super(AudioTailClipSlot, self).record, bar_length=bar_length))
        # seq.add(self.add_stop_button)
        # seq.add(wait=1)
        # seq.add(self.fire)
        seq.add(partial(self.wait_for_silence, bar_length=bar_length))
        # seq.add(partial(self._call_post_record, bar_length=bar_length))
        return seq.done()

    # def _call_post_record(self, bar_length):
    #     # type: (int) -> None
    #     seq = Sequence()
    #     seq.add(complete_on=lambda: self.clip.is_recording_listener, no_timeout=True)
    #     seq.add(partial(self.post_record, bar_length=bar_length))
    #     seq.done()

    # def post_record(self, bar_length):
    #     # type: (int) -> None
    #     self.clip.clip_name.update(base_name="")
    #     clip_end = bar_length * self.song.signature_numerator
    #
    #     self.clip.start_marker = self.clip.loop_start = clip_end
    #     self.clip.looping = False
    #     self.clip.muted = True
