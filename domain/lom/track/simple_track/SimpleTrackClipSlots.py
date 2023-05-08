import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager
from typing import List, Type, Optional, Iterator

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.clip_slot.ClipSlotHasClipEvent import ClipSlotHasClipEvent
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.simple_track.SimpleTrackClips import SimpleTrackClips
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class SimpleTrackClipSlots(SlotManager, Observable):
    # noinspection PyInitNewSignature
    def __init__(self, live_track, clip_slot_class, clip_config, track_devices):
        # type: (Live.Track.Track, Type[ClipSlot], ClipConfig, SimpleTrackDevices) -> None
        super(SimpleTrackClipSlots, self).__init__()
        self._live_track = live_track
        self._clip_slot_class = clip_slot_class

        self._clip_slots = []  # type: List[ClipSlot]

        self._clips = SimpleTrackClips(self, track_devices, live_track.color_index)
        self._has_clip_listener.replace_subjects(live_track.clip_slots)

        self._instrument = None  # type: Optional[InstrumentInterface]
        self._clip_config = clip_config

    def __iter__(self):
        # type: () -> Iterator[ClipSlot]
        return iter(self._clip_slots)

    def set_instrument(self, instrument):
        # type: (Optional[InstrumentInterface]) -> None
        self._instrument = instrument

        if self._instrument:
            self._clip_config.default_note = self._instrument.DEFAULT_NOTE

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return self._clip_slots

    @property
    def clips(self):
        # type: () -> List[Clip]
        return list(self._clips)

    @property
    def selected(self):
        # type: () -> ClipSlot
        return list(self._clip_slots)[Song.selected_scene().index]

    @property
    def playing_clip(self):
        # type: () -> Optional[Clip]
        clip_slot = find_if(lambda cs: cs.is_playing, self._clip_slots)
        return clip_slot.clip if clip_slot is not None else None

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
                if clip_slot.clip is not None:
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
            self.notify_observers()

    @subject_slot_group("has_clip")
    @defer
    def _has_clip_listener(self, clip_slot):
        # type: (Live.ClipSlot.ClipSlot) -> None
        DomainEventBus.emit(ClipSlotHasClipEvent(self._live_track))
        # noinspection PyBroadException
        try:
            if clip_slot.clip:
                clip_slot.clip.color_index = self._live_track.color_index
        except Exception:
            pass

    def toggle_colors(self):
        # type: () -> None
        self._clips.clip_color_manager.toggle_colors()

    def disconnect(self):
        # type: () -> None
        super(SimpleTrackClipSlots, self).disconnect()
        for clip_slot in self.clip_slots:
            clip_slot.disconnect()
