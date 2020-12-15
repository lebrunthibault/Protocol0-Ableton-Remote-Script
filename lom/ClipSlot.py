from typing import Any, TYPE_CHECKING

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
        self.has_clip = False
        self.clip = None  # type: Clip
        self.update_clip.subject = self._clip_slot
        self.update_clip()

    def __nonzero__(self):
        return self._clip_slot is not None

    @subject_slot("has_clip")
    def update_clip(self):
        self.has_clip = self._clip_slot.has_clip
        self.clip = Clip(clip_slot=self) if self.has_clip else None

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
