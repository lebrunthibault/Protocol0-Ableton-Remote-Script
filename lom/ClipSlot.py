from typing import Any, Optional, TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Clip import Clip

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class ClipSlot(AbstractObject):
    def __init__(self, clip_slot, index, track, *a, **k):
        # type: (Live.ClipSlot.ClipSlot, int, SimpleTrack, Any, Any) -> None
        super(ClipSlot, self).__init__(*a, **k)
        self._clip_slot = clip_slot
        self.track = track
        self.index = index

    def __nonzero__(self):
        return self._clip_slot is not None

    def __eq__(self, other):
        if isinstance(other, ClipSlot):
            return self._clip_slot == other._clip_slot
        return False

    @property
    def is_triggered(self):
        # type: () -> bool
        return self._clip_slot.is_triggered

    @property
    def has_clip(self):
        # type: () -> bool
        return self._clip_slot.has_clip

    @property
    def clip(self):
        # type: () -> Optional[Clip]
        return Clip(clip_slot=self._clip_slot, index=self.index, track=self.track) if self.has_clip else None

    def fire(self, record_length):
        # type: (int) -> None
        self._clip_slot.fire(record_length=record_length)
