from functools import partial

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Any, Optional, Type

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.domain.lom.clip.ClipCreatedOrDeletedEvent import ClipCreatedOrDeletedEvent
from protocol0.domain.lom.clip.ClipSlotSelectedEvent import ClipSlotSelectedEvent
from protocol0.domain.lom.clip_slot.ClipSlotAppearance import ClipSlotAppearance
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class ClipSlot(SlotManager, Observable):
    CLIP_CLASS = Clip  # type: Type[Clip]

    def __init__(self, live_clip_slot, index, clip_config):
        # type: (Live.ClipSlot.ClipSlot, int, ClipConfig) -> None
        super(ClipSlot, self).__init__()
        self._clip_slot = live_clip_slot
        self._index = index
        self._clip_config = clip_config
        self.appearance = ClipSlotAppearance(live_clip_slot)

        self._has_clip_listener.subject = self._clip_slot
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
        return "%s (%s)" % (self.__class__.__name__, self.clip.name if self.clip else "empty")

    @subject_slot("has_clip")
    def _has_clip_listener(self):
        # type: () -> None
        self._map_clip(is_new=True)

        DomainEventBus.emit(ClipCreatedOrDeletedEvent(self._clip_slot))
        self.notify_observers()

        Scheduler.defer(self.appearance.refresh)

    def _map_clip(self, is_new=False):
        # type: (bool) -> None
        if self.has_clip:
            self.clip = self.CLIP_CLASS(self._clip_slot.clip, self.index, self._clip_config)

            if is_new:
                self.clip.on_added()

            self.clip.register_observer(self)
        else:
            if self.clip is not None:
                self.clip.disconnect()

            self.clip = None

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, Clip):
            if observable.deleted:
                self.delete_clip()
            elif observable.selected:
                self.select()

    @property
    def has_clip(self):
        # type: () -> bool
        return self._clip_slot and self._clip_slot.has_clip

    @property
    def index(self):
        # type: () -> int
        return self._index

    @index.setter
    def index(self, index):
        # type: (int) -> None
        self._index = index
        if self.clip:
            self.clip.index = index

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

    def select(self):
        # type: () -> None
        DomainEventBus.emit(ClipSlotSelectedEvent(self._clip_slot))

    def delete_clip(self):
        # type: () -> Sequence
        seq = Sequence()
        if self._clip_slot and self.has_clip and self.clip:
            seq.add(self._clip_slot.delete_clip)
            seq.wait_for_event(ClipCreatedOrDeletedEvent, self._clip_slot)
        return seq.done()


    def prepare_for_record(self):
        # type: () -> Sequence
        seq = Sequence()
        if self.clip:
            seq.add(self.delete_clip)
            seq.wait(3)  # because has stop button is automatically removed on deletion

        seq.add(partial(setattr, self.appearance, "has_stop_button", True))
        seq.defer()
        return seq.done()

    def create_clip(self):
        # type: () -> Optional[Sequence]
        """creating one bar clip"""
        if self._clip_slot is None:
            return None
        from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot

        if not isinstance(self, MidiClipSlot):
            raise Protocol0Warning("Clips can only be created on midi tracks")
        if self.clip:
            raise Protocol0Warning("%s has already a clip" % self)

        seq = Sequence()
        seq.add(partial(self._clip_slot.create_clip, Song.signature_numerator()))
        seq.wait_for_event(ClipCreatedOrDeletedEvent, self._clip_slot)
        seq.defer()
        seq.add(lambda: self.clip.clip_name._name_listener())
        return seq.done()

    def duplicate_clip_to(self, clip_slot):
        # type: (ClipSlot) -> Sequence
        seq = Sequence()
        if self._clip_slot:
            seq.add(partial(self._clip_slot.duplicate_clip_to, clip_slot._clip_slot))
            seq.wait_for_event(ClipCreatedOrDeletedEvent, clip_slot._clip_slot)
            seq.defer()
        return seq.done()

    def disconnect(self):
        # type: () -> None
        super(ClipSlot, self).disconnect()
        if self.clip:
            self.clip.disconnect()
