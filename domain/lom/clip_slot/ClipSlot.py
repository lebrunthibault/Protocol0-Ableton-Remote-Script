from functools import partial

import Live
from typing import Any, TYPE_CHECKING, Optional

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipCreatedEvent import ClipCreatedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackFirstClipAddedEvent import SimpleTrackFirstClipAddedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackLastClipDeletedEvent import SimpleTrackLastClipDeletedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class ClipSlot(UseFrameworkEvents):
    __subject_events__ = ("has_clip", "is_triggered")

    CLIP_CLASS = Clip

    def __init__(self, clip_slot, track):
        # type: (Live.ClipSlot.ClipSlot, SimpleTrack) -> None
        super(ClipSlot, self).__init__()
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
        return "%s (%s)" % (self.__class__.__name__, self.clip.name if self.clip else "empty (of %s)" % self.track.name)

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

        if self.has_clip and len(self.track.clips) == 1:
            DomainEventBus.notify(SimpleTrackFirstClipAddedEvent())
        elif not self.has_clip and len(self.track.clips) == 0:
            DomainEventBus.notify(SimpleTrackLastClipDeletedEvent())

        DomainEventBus.notify(ClipCreatedEvent())

        if not self.clip and self.has_stop_button:
            Scheduler.defer(partial(setattr, self, "has_stop_button", False))

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
        if self._clip_slot and self.has_clip and self.clip:
            seq.add(self._clip_slot.delete_clip)
            seq.wait_for_listener(self.has_clip_listener)  # type: ignore[arg-type]
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

    def fire(self):
        # type: () -> None
        self._clip_slot.fire()

    def prepare_for_record(self):
        # type: () -> Sequence
        seq = Sequence()
        if self.clip:
            seq.add(self.delete_clip)
            seq.wait(3)  # because has stop button is automatically removed on deletion

        seq.add(partial(setattr, self, "has_stop_button", True))
        seq.defer()
        return seq.done()

    def create_clip(self):
        # type: () -> Optional[Sequence]
        """ creating one bar clip """
        if self._clip_slot is None:
            return None
        from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
        if not isinstance(self, MidiClipSlot):
            raise Protocol0Warning("Clips can only be created on midi tracks")
        if self.clip:
            raise Protocol0Warning("%s has already a clip" % self)

        seq = Sequence()
        seq.add(partial(self._clip_slot.create_clip, SongFacade.signature_numerator()))
        seq.wait_for_listener(self.has_clip_listener)  # type: ignore[arg-type]
        seq.defer()
        seq.add(lambda: self.clip.select())
        seq.add(lambda: self.clip.clip_name._name_listener())
        return seq.done()

    def duplicate_clip_to(self, clip_slot):
        # type: (ClipSlot) -> Sequence
        seq = Sequence()
        if self._clip_slot:
            seq.add(partial(self._clip_slot.duplicate_clip_to, clip_slot._clip_slot))
            seq.wait_for_listener(clip_slot.has_clip_listener)  # type: ignore[arg-type]
            seq.defer()
        return seq.done()

    def disconnect(self):
        # type: () -> None
        super(ClipSlot, self).disconnect()
        if self.clip:
            self.clip.disconnect()
