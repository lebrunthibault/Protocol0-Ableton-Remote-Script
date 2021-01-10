import Live
from typing import Any, TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.utils.decorators import has_callback_queue

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
        self.register_slot(self._clip_slot, self._has_clip_listener, "has_clip")  # allows subclassing
        self._map_clip()

    def __nonzero__(self):
        return self._clip_slot is not None

    def __eq__(self, clip_slot):
        # type: (ClipSlot) -> bool
        return clip_slot and self._clip_slot == clip_slot._clip_slot

    @staticmethod
    def make_clip_slot(clip_slot, index, track):
        # type: (Live.ClipSlot.ClipSlot, int, SimpleTrack) -> ClipSlot
        from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
        from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
        if isinstance(track, AutomationMidiTrack):
            return AutomationMidiClipSlot(clip_slot=clip_slot, index=index, track=track)
        else:
            return ClipSlot(clip_slot=clip_slot, index=index, track=track)

    def _map_clip(self):
        self.has_clip = self._clip_slot.has_clip
        self.clip = None
        if self.has_clip:
            self.clip = Clip.make_clip(clip_slot=self)

    @has_callback_queue
    def _has_clip_listener(self):
        self.parent.log_debug("has_clip in ClipSlot")
        self._map_clip()
        if self.song.highlighted_clip_slot == self and self.has_clip:
            self.parent._wait(2, self.parent.push2Manager.update_clip_grid_quantization)
        self.parent.log_debug(self.clip)

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

    def duplicate_clip_to(self, clip_slot):
        # type: (ClipSlot) -> None
        self._clip_slot.duplicate_clip_to(clip_slot._clip_slot)

    def insert_dummy_clip(self):
        self.song.tracks[0].clip_slots[0].duplicate_clip_to(self)
