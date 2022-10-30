from functools import partial

from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AudioClipSlot(ClipSlot):
    CLIP_CLASS = AudioClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioClip]

    def replace_clip(self, source_clip_slot):
        # type: (AudioClipSlot) -> Sequence
        Logger.info("Replacing %s with %s" % (self.clip, source_clip_slot.clip))

        clip_looping = self.clip.looping

        seq = Sequence()
        seq.add(partial(source_clip_slot.duplicate_clip_to, self))
        seq.add(lambda: setattr(self.clip, "looping", clip_looping))

        return seq.done()
