from functools import partial

from typing import Any, TYPE_CHECKING, Optional

import Live
from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.clip.Clip import Clip
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class ClipSlot(AbstractObject):
    __subject_events__ = ("has_clip", "is_triggered", "stopped")

    CLIP_CLASS = Clip

    def __init__(self, clip_slot, track, *a, **k):
        # type: (Live.ClipSlot.ClipSlot, SimpleTrack, Any, Any) -> None
        super(ClipSlot, self).__init__(*a, **k)
        self._clip_slot = clip_slot
        self.track = track
        self._has_clip_listener.subject = self._clip_slot
        self._is_triggered_listener.subject = self._clip_slot
        self.clip = None  # type: Optional[Clip]
        self._map_clip()

    def __nonzero__(self):
        # type: () -> bool
        return self._clip_slot is not None

    def __eq__(self, clip_slot):
        # type: (object) -> bool
        return isinstance(clip_slot, ClipSlot) and self._clip_slot == clip_slot._clip_slot

    def __repr__(self):
        # type: () -> str
        out = super(ClipSlot, self).__repr__()
        return "%s (%s)" % (out, self.clip.name if self.clip else "empty (of %s)" % self.track.base_name)

    @staticmethod
    def make(clip_slot, track):
        # type: (Live.ClipSlot.ClipSlot, SimpleTrack) -> ClipSlot
        return track.CLIP_SLOT_CLASS(clip_slot=clip_slot, track=track)

    @p0_subject_slot("has_clip")
    def _has_clip_listener(self):
        # type: () -> None
        if self.clip:
            self.clip.disconnect()

        self._map_clip(is_new=True)

    def _map_clip(self, is_new=False):
        # type: (bool) -> None
        self.clip = Clip.make(clip_slot=self, is_new=is_new) if self.has_clip else None

        # noinspection PyUnresolvedReferences
        self.notify_has_clip()

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        self.notify_is_triggered()

    def refresh_appearance(self):
        # type: () -> None
        self.has_stop_button = False

    @property
    def has_clip(self):
        # type: () -> bool
        return self._clip_slot and self._clip_slot.has_clip

    @property
    def has_stop_button(self):
        # type: () -> bool
        return self._clip_slot and self._clip_slot.has_stop_button

    @has_stop_button.setter
    def has_stop_button(self, has_stop_button):
        # type: (bool) -> None
        if self._clip_slot:
            self._clip_slot.has_stop_button = has_stop_button

    def delete_clip(self):
        # type: () -> None
        if self._clip_slot and self._clip_slot.has_clip:
            self._clip_slot.delete_clip()

    @property
    def index(self):
        # type: () -> int
        return self.track.clip_slots.index(self)

    @property
    def is_triggered(self):
        # type: () -> bool
        return self._clip_slot and self._clip_slot.is_triggered

    @property
    def is_playing(self):
        # type: () -> bool
        return self._clip_slot and self._clip_slot.is_playing

    def record(self, bar_length, bar_tail_length):
        # type: (int, int) -> Optional[Sequence]
        seq = Sequence()
        if not self.has_stop_button:
            self.has_stop_button = True
            seq.add(wait=1)

        if bar_length == 0:
            self.parent.show_message("Starting recording of %s" % BarLengthEnum.UNLIMITED)
            seq.add(self.fire, complete_on=self._has_clip_listener)
        else:
            bar_legend = "%d" % bar_length
            if bar_tail_length:
                bar_legend += " (+%d)" % bar_tail_length
            self.parent.show_message("Starting recording of %s bars" % bar_legend)
            seq.add(wait=1)  # necessary so that _has_clip_listener triggers on has_clip == True
            seq.add(
                partial(self.fire, record_length=self.parent.utilsManager.get_beat_time(bar_length + bar_tail_length)),
                complete_on=self._has_clip_listener,
            )

        # noinspection PyUnresolvedReferences
        seq.add(self.track.abstract_track.notify_is_recording)

        seq.add(
            complete_on=lambda: self.clip._is_recording_listener,
            name="awaiting clip recording end",
            no_timeout=True,
        )

        if bar_tail_length:
            seq.add(wait=1)
            seq.add(lambda: self.clip.post_record_clip_tail(bar_tail_length=bar_tail_length))

        return seq.done()

    def fire(self, record_length=None):
        # type: (Optional[int]) -> None
        if self._clip_slot is None:
            return None

        if record_length:
            self._clip_slot.fire(record_length=record_length)
        else:
            self._clip_slot.fire()

    def duplicate_clip_to(self, clip_slot):
        # type: (ClipSlot) -> Sequence
        seq = Sequence()
        if self._clip_slot:
            seq.add(
                partial(self._clip_slot.duplicate_clip_to, clip_slot._clip_slot),
                complete_on=clip_slot._has_clip_listener,
            )
        return seq.done()

    def disconnect(self):
        # type: () -> None
        super(ClipSlot, self).disconnect()
        if self.clip:
            self.clip.disconnect()
