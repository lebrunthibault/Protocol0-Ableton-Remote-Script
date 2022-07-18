import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager
from typing import List, Type, Optional, Iterator

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.simple_track.SimpleTrackFirstClipAddedEvent import (
    SimpleTrackFirstClipAddedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrackLastClipDeletedEvent import (
    SimpleTrackLastClipDeletedEvent,
)
from protocol0.domain.shared.decorators import defer
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable


class SimpleTrackClipSlots(SlotManager):
    def __init__(self, live_track, clip_slot_class):
        # type: (Live.Track.Track, Type[ClipSlot]) -> None
        super(SimpleTrackClipSlots, self).__init__()
        self._live_track = live_track
        self._clip_slot_class = clip_slot_class

        self._clip_slots = []  # type: List[ClipSlot]

        self._has_clip_listener.replace_subjects(live_track.clip_slots)

        self._instrument = None  # type: Optional[InstrumentInterface]
        self._clip_config = ClipConfig(self._live_track.color_index)

    def __iter__(self):
        # type: () -> Iterator[ClipSlot]
        return iter(self._clip_slots)

    def set_instrument(self, instrument):
        # type: (Optional[InstrumentInterface]) -> None
        self._instrument = instrument

        if self._instrument:
            self._clip_config.uses_scene_length_clips = self._instrument.uses_scene_length_clips
            self._clip_config.default_note = self._instrument.DEFAULT_NOTE

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return self._clip_slots

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [
            clip_slot.clip for clip_slot in self.clip_slots if clip_slot.has_clip and clip_slot.clip
        ]

    @property
    def selected(self):
        # type: () -> ClipSlot
        return list(self._clip_slots)[SongFacade.selected_scene().index]

    def build(self):
        # type: () -> None
        """create new ClipSlot objects and keep existing ones"""
        live_cs_to_cs = {cs._clip_slot: cs for cs in self.clip_slots}

        new_clip_slots = []  # type: List[ClipSlot]
        for (index, live_clip_slot) in enumerate(list(self._live_track.clip_slots)):
            if live_clip_slot in live_cs_to_cs:
                clip_slot = live_cs_to_cs[live_clip_slot]
                # reindexing is necessary
                clip_slot.index = index
                if clip_slot.clip:
                    clip_slot.clip.index = index
                new_clip_slots.append(clip_slot)
            else:
                clip_slot = self._clip_slot_class(live_clip_slot, index, self._clip_config)
                clip_slot.register_observer(self)
                new_clip_slots.append(clip_slot)
        self._clip_slots[:] = new_clip_slots  # type: List[ClipSlot]

        for cs in self._clip_slots:
            Scheduler.defer(cs.appearance.refresh)

        self._has_clip_listener.replace_subjects(self._live_track.clip_slots)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, ClipSlot):
            if observable.has_clip and len(self.clips) == 1:
                DomainEventBus.emit(SimpleTrackFirstClipAddedEvent())
            elif not observable.has_clip and len(self.clips) == 0:
                DomainEventBus.emit(SimpleTrackLastClipDeletedEvent())

    @subject_slot_group("has_clip")
    @defer
    def _has_clip_listener(self, clip_slot):
        # type: (Live.ClipSlot.ClipSlot) -> None
        if clip_slot.clip:
            clip_slot.clip.color_index = self._live_track.color_index

    def disconnect(self):
        # type: () -> None
        super(SimpleTrackClipSlots, self).disconnect()
        for clip_slot in self.clip_slots:
            clip_slot.disconnect()
