from functools import partial

from typing import Any, TYPE_CHECKING, Optional

import Live
from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class ClipSlot(AbstractObject):
    __subject_events__ = ("has_clip", "is_triggered")

    CLIP_CLASS = Clip

    def __init__(self, clip_slot, track, *a, **k):
        # type: (Live.ClipSlot.ClipSlot, SimpleTrack, Any, Any) -> None
        super(ClipSlot, self).__init__(*a, **k)
        self._clip_slot = clip_slot
        self.track = track
        self.has_clip_listener.subject = self._clip_slot
        self._is_triggered_listener.subject = self._clip_slot
        self.clip = None  # type: Optional[Clip]
        self._map_clip()

    def __nonzero__(self):
        # type: () -> bool
        return self._clip_slot is not None

    def __eq__(self, clip_slot):
        # type: (object) -> bool
        return isinstance(clip_slot, ClipSlot) and self._clip_slot == clip_slot._clip_slot

    def __repr__(self, **k):
        # type: (Any) -> str
        out = super(ClipSlot, self).__repr__()
        return "%s (%s)" % (out, self.clip.name if self.clip else "empty (of %s)" % self.track.name)

    @staticmethod
    def make(clip_slot, track):
        # type: (Live.ClipSlot.ClipSlot, SimpleTrack) -> ClipSlot
        return track.CLIP_SLOT_CLASS(clip_slot=clip_slot, track=track)

    @p0_subject_slot("has_clip")
    def has_clip_listener(self):
        # type: () -> None
        if self.clip:
            self.clip.disconnect()

        self._map_clip(is_new=True)

        if not self.clip and self.has_stop_button:
            self.parent.defer(partial(setattr, self, "has_stop_button", False))

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
        # type: () -> Sequence
        seq = Sequence()
        if self._clip_slot and self.clip:
            seq.add(self._clip_slot.delete_clip, complete_on=self.has_clip_listener)
        return seq.done()

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

    def prepare_for_record(self):
        # type: () -> Sequence
        seq = Sequence()
        if self.clip:
            seq.add(self.delete_clip)
            seq.add(wait=3)  # because has stop button is automatically removed on deletion

        seq.add(partial(setattr, self, "has_stop_button", True))
        seq.add(wait=1)
        return seq.done()

    def create_clip(self):
        # type: () -> Optional[Sequence]
        """ creating one bar clip """
        if self._clip_slot is None:
            return None
        if self.clip:
            self.parent.log_error("%s has already a clip" % self)
            return None

        seq = Sequence()
        seq.add(partial(self._clip_slot.create_clip, self.song.signature_numerator),
                complete_on=self.has_clip_listener)
        seq.add(lambda: self.clip.clip_name._name_listener())
        return seq.done()

    def duplicate_clip_to(self, clip_slot):
        # type: (ClipSlot) -> Sequence
        seq = Sequence()
        if self._clip_slot:
            seq.add(
                partial(self._clip_slot.duplicate_clip_to, clip_slot._clip_slot),
                complete_on=clip_slot.has_clip_listener,
            )
        return seq.done()

    def disconnect(self):
        # type: () -> None
        super(ClipSlot, self).disconnect()
        if self.clip:
            self.clip.disconnect()
