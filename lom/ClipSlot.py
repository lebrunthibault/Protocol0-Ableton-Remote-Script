from typing import Any, TYPE_CHECKING

import Live
from _Framework.SubjectSlot import subject_slot
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
        self.has_clip = clip_slot.has_clip
        self.clip = None  # type: Clip
        self._has_clip_listener.subject = self._clip_slot
        self._has_clip_listener()

    def __nonzero__(self):
        return self._clip_slot is not None

    def __eq__(self, clip_slot):
        # type: (ClipSlot) -> bool
        return clip_slot and self._clip_slot == clip_slot._clip_slot

    @subject_slot("has_clip")
    def _has_clip_listener(self):
        self.has_clip = self._clip_slot.has_clip
        self.clip = Clip(clip_slot=self) if self.has_clip else None
        if self.clip and hasattr(self.track, "_on_clip_creation"):
            self.track._on_clip_creation(self.clip)

    def delete_clip(self):
        if self._clip_slot.has_clip:
            return self._clip_slot.delete_clip()

    @property
    def is_triggered(self):
        # type: () -> bool
        return self._clip_slot.is_triggered

    def fire(self, record_length):
        # type: (int) -> None
        self._clip_slot.fire(record_length=record_length)
