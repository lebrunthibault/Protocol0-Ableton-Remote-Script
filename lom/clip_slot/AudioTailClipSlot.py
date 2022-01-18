from functools import partial

from typing import Any, Optional

from protocol0.lom.clip.AudioTailClip import AudioTailClip
from protocol0.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot


class AudioTailClipSlot(AudioClipSlot):
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

    def wait_for_silence(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(partial(setattr, self._beat_changed_listener, "subject", self.parent.beatScheduler))
        seq.add(complete_on=self._is_silent_listener, no_timeout=True)
        seq.add(partial(setattr, self._beat_changed_listener, "subject", None))
        return seq.done()

    def record(self, bar_length):
        # type: (int) -> Sequence
        seq = Sequence()
        seq.add(partial(super(AudioTailClipSlot, self).fire, bar_length=bar_length))
        seq.add(self.wait_for_silence)
        return seq.done()
