from typing import Any, TYPE_CHECKING

import Live

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.utils.decorators import subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


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
        self._map_clip()

    def __nonzero__(self):
        return self._clip_slot is not None

    def __eq__(self, clip_slot):
        # type: (ClipSlot) -> bool
        return clip_slot and self._clip_slot == clip_slot._clip_slot

    def _map_clip(self):
        self.has_clip = self._clip_slot.has_clip
        self.clip = Clip(clip_slot=self) if self.has_clip else None
        self.track._clip_notes_listener.replace_subjects([clip._clip for clip in self.track.clips])

    @subject_slot("has_clip")
    def _has_clip_listener(self):
        self._map_clip()
        if self.song.highlighted_clip_slot == self and self.has_clip:
            self.parent._wait(2, self.parent.push2Manager.update_clip_grid_quantization)

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
