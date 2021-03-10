from functools import partial

import Live
from typing import Any, TYPE_CHECKING, Optional

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot, is_change_deferrable

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class ClipSlot(AbstractObject):
    __subject_events__ = ("has_clip", "is_triggered")

    def __init__(self, clip_slot, index, track, *a, **k):
        # type: (Live.ClipSlot.ClipSlot, int, SimpleTrack, Any, Any) -> None
        super(ClipSlot, self).__init__(*a, **k)
        self._clip_slot = clip_slot
        self.track = track
        self.index = index
        self._has_clip_listener.subject = self._clip_slot
        self._is_triggered_listener.subject = self._clip_slot
        self.linked_clip_slot = None  # type: Optional[ClipSlot]
        self.clip = None  # type: Optional[Clip]
        self._has_clip_listener()

    def __nonzero__(self):
        return self._clip_slot is not None

    def __eq__(self, clip_slot):
        # type: (ClipSlot) -> bool
        return clip_slot and self._clip_slot == clip_slot._clip_slot

    def __repr__(self):
        repr = super(ClipSlot, self).__repr__()
        return "%s (%s)" % (repr, self.clip.name if self.has_clip else "empty (of %s)" % self.track.base_name)

    @staticmethod
    def make(clip_slot, index, track):
        # type: (Live.ClipSlot.ClipSlot, int, SimpleTrack) -> ClipSlot
        from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
        from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
        if isinstance(track, AutomationMidiTrack):
            return AutomationMidiClipSlot(clip_slot=clip_slot, index=index, track=track)
        else:
            return ClipSlot(clip_slot=clip_slot, index=index, track=track)

    @p0_subject_slot("has_clip")
    def _has_clip_listener(self):
        if self.clip:
            self.clip.disconnect()

        self.clip = Clip.make(clip_slot=self) if self.has_clip else None

        self.parent.log_debug("has clip !")

        # noinspection PyUnresolvedReferences
        self.notify_has_clip()

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        self.parent.log_debug("is_triggered !")
        # noinspection PyUnresolvedReferences
        self.notify_is_triggered()

    @property
    def has_clip(self):
        return self._clip_slot.has_clip

    @is_change_deferrable
    def delete_clip(self):
        if self._clip_slot.has_clip:
            self._clip_slot.delete_clip()

    @property
    def is_triggered(self):
        # type: () -> bool
        return self._clip_slot.is_triggered

    @property
    def is_playing(self):
        # type: () -> bool
        return self._clip_slot.is_playing

    def record(self):
        seq = Sequence()
        self.parent.show_message("Starting recording of %d bars" % self.song.recording_bar_count)
        seq.add(partial(self.fire, record_length=self.parent.utilsManager.get_beat_time(self.song.recording_bar_count)),
                complete_on=self._has_clip_listener)
        seq.add(complete_on=lambda: self.clip._is_recording_listener, no_timeout=True,
                name="awaiting clip recording end")
        return seq.done()

    def fire(self, record_length):
        # type: (int) -> None
        self._clip_slot.fire(record_length=record_length)

    def duplicate_clip_to(self, clip_slot):
        # type: (ClipSlot) -> None
        seq = Sequence()
        seq.add(partial(self._clip_slot.duplicate_clip_to, clip_slot._clip_slot),
                complete_on=clip_slot._has_clip_listener)
        return seq.done()

    @is_change_deferrable
    def insert_dummy_clip(self, name):
        # type: (str) -> None
        seq = Sequence()
        seq.add(partial(self.song.simple_tracks[0].clip_slots[0].duplicate_clip_to, self),
                complete_on=self._has_clip_listener)
        seq.add(lambda: setattr(self.clip, "warping", 1), name="enable clip warping")
        seq.add(lambda: setattr(self.clip, "looping", 1), name="enable clip looping")
        seq.add(wait=2)  # should be 2 because the created dummy clip name syncs to the midi clip
        seq.add(lambda: setattr(self.clip, "name", name))
        return seq.done()

    def disconnect(self):
        super(ClipSlot, self).disconnect()
        if self.clip:
            self.clip.disconnect()
