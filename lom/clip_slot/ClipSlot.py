from functools import partial

import Live
from typing import Any, TYPE_CHECKING

from _Framework.Util import find_if
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import subject_slot
from a_protocol_0.utils.utils import find_last

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
        self.clip_name = None
        self._map_clip()

    def __nonzero__(self):
        return self._clip_slot is not None

    def __repr__(self):
        repr = super(ClipSlot, self).__repr__()
        return "%s (%s)" % (repr, self.track)

    def __eq__(self, clip_slot):
        # type: (ClipSlot) -> bool
        return clip_slot and self._clip_slot == clip_slot._clip_slot

    @staticmethod
    def make(clip_slot, index, track):
        # type: (Live.ClipSlot.ClipSlot, int, SimpleTrack) -> ClipSlot
        from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
        from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
        from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
        from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot
        if isinstance(track, AutomationMidiTrack):
            return AutomationMidiClipSlot(clip_slot=clip_slot, index=index, track=track)
        elif isinstance(track, AutomationAudioTrack):
            return AutomationAudioClipSlot(clip_slot=clip_slot, index=index, track=track)
        else:
            return ClipSlot(clip_slot=clip_slot, index=index, track=track)

    def _map_clip(self):
        self.has_clip = self._clip_slot.has_clip
        self.clip = None
        if self.has_clip:
            self.clip = Clip.make(clip_slot=self)

    @subject_slot("has_clip")
    def _has_clip_listener(self):
        self._map_clip()
        if self.song.highlighted_clip_slot == self and self.has_clip:
            self.parent._wait(2, self.parent.push2Manager.update_clip_grid_quantization)
        other_clip_slot = find_last(lambda cs: cs.has_clip and cs.index < self.index, self.track.clip_slots) or find_if(lambda cs: cs.has_clip, self.track.clip_slots)
        if other_clip_slot:
            self.track.track_name.set(clip_slot_index=other_clip_slot.index, notify_base_name=False)

    def delete_clip(self):
        seq = Sequence()
        if self._clip_slot.has_clip:
            seq.add(wait=1)
            seq.add(self._clip_slot.delete_clip)
        return seq.done()

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
        seq = Sequence()
        seq.add(partial(self.song.simple_tracks[0].clip_slots[0].duplicate_clip_to, self), complete_on=self._has_clip_listener)
        seq.add(lambda: setattr(self.clip, "warping", 1), name="enable clip warping")
        seq.add(wait=1)
        seq.add(lambda: setattr(self.clip, "looping", 1), name="enable clip looping")
        return seq.done()

    def disconnect(self):
        super(ClipSlot, self).disconnect()
        if self.clip:
            self.clip.disconnect()
