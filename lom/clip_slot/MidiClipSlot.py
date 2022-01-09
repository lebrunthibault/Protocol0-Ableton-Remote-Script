from functools import partial

from typing import Any, Optional

from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.sequence.Sequence import Sequence


class MidiClipSlot(ClipSlot):
    CLIP_CLASS = MidiClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MidiClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[MidiClip]

    def record(self, bar_length, record_tail=False):
        # type: (int, bool) -> Optional[Sequence]
        seq = Sequence()
        seq.add(partial(super(MidiClipSlot, self).record, bar_length=bar_length))
        if record_tail and InterfaceState.SELECTED_RECORDING_BAR_LENGTH == BarLengthEnum.UNLIMITED:
            seq.add(wait=1)
            seq.add(self.post_record_clip_tail)

        return seq.done()

    def post_record_clip_tail(self):
        # type: () -> None
        clip_end = self.clip.end_marker - self.song.signature_numerator
        self.clip.loop_end = clip_end
        self.clip.end_marker = clip_end
