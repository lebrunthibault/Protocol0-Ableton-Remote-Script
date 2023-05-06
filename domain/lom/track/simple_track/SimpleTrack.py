from functools import partial

import Live
from _Framework.SubjectSlot import subject_slot
from typing import cast, List, Optional, Dict

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.clip.ClipTail import ClipTail
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.InstrumentFactory import InstrumentFactory
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.routing.TrackInputRouting import TrackInputRouting
from protocol0.domain.lom.track.routing.TrackOutputRouting import TrackOutputRouting
from protocol0.domain.lom.track.simple_track.SimpleTrackArmState import SimpleTrackArmState
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots
from protocol0.domain.lom.track.simple_track.SimpleTrackCreatedEvent import SimpleTrackCreatedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackDeletedEvent import SimpleTrackDeletedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import (
    SimpleTrackFlattenedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrackMonitoringState import (
    SimpleTrackMonitoringState,
)
from protocol0.domain.lom.track.simple_track.SimpleTrackSaveStartedEvent import (
    SimpleTrackSaveStartedEvent,
)
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.utils import volume_to_db, db_to_volume
from protocol0.shared.Config import Config
from protocol0.shared.Song import Song
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class SimpleTrack(AbstractTrack):
    # is_active is used to differentiate set tracks for return / master
    # we act only on active tracks
    IS_ACTIVE = True
    CLIP_SLOT_CLASS = ClipSlot

    # noinspection PyInitNewSignature
    def __init__(self, live_track, index):
        # type: (Live.Track.Track, int) -> None
        self._track = live_track  # type: Live.Track.Track
        self._index = index

        super(SimpleTrack, self).__init__(self)

        self.live_id = live_track._live_ptr  # type: int
        DomainEventBus.emit(SimpleTrackCreatedEvent(self))
        # Note : SimpleTracks represent the first layer of abstraction and know nothing about
        # AbstractGroupTracks except with self.abstract_group_track which links both layers
        # and is handled by the abg
        self.group_track = self.group_track  # type: Optional[SimpleTrack]
        if self.group_track is not None:
            self.color = self.group_track.color

        self.sub_tracks = []  # type: List[SimpleTrack]

        self._instrument = None  # type: Optional[InstrumentInterface]
        self._view = live_track.view

        self.devices = SimpleTrackDevices(live_track)
        self.devices.register_observer(self)

        self._clip_config = ClipConfig(self.color)
        self._clip_slots = SimpleTrackClipSlots(
            live_track, self.CLIP_SLOT_CLASS, self._clip_config, self.devices
        )
        self._clip_slots.build()
        self._clip_slots.register_observer(self)
        self.clip_tail = ClipTail(self._clip_slots)

        self.monitoring_state = SimpleTrackMonitoringState(self)

        self.input_routing = TrackInputRouting(self._track)
        self.output_routing = TrackOutputRouting(self._track)

        self.arm_state = SimpleTrackArmState(live_track)
        self.arm_state.register_observer(self)

        self._output_meter_level_listener.subject = None

        self.devices.build()

    device_insert_mode = cast(int, ForwardTo("_view", "device_insert_mode"))

    def on_tracks_change(self):
        # type: () -> None
        self._link_to_group_track()
        # because we traverse the tracks left to right : sub tracks will register themselves
        if self.is_foldable:
            self.sub_tracks[:] = []

    def on_scenes_change(self):
        # type: () -> None
        self._clip_slots.build()

    def _link_to_group_track(self):
        # type: () -> None
        """
        1st layer linking
        Connect to the enclosing simple group track is any
        """
        if self._track.group_track is None:
            self.group_track = None
            return None

        self.group_track = Song.live_track_to_simple_track(self._track.group_track)
        self.group_track.add_or_replace_sub_track(self)
        if self.group_track.color != self.color:
            # working around live setting the group track to the default color
            Scheduler.wait(2, lambda: setattr(self, "color", self.group_track.color))

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return list(self._clip_slots)

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [
            clip_slot.clip
            for clip_slot in self.clip_slots
            if clip_slot.has_clip and clip_slot.clip is not None
        ]

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, SimpleTrackDevices):
            # Refreshing is only really useful from simpler devices that change when a new sample is loaded
            if self.IS_ACTIVE and not self.is_foldable:
                self.instrument = InstrumentFactory.make_instrument_from_simple_track(
                    self.devices, self.instrument, self.abstract_track.name
                )
        elif isinstance(observable, SimpleTrackArmState) and self.arm_state.is_armed:
            DomainEventBus.emit(SimpleTrackArmedEvent(self._track))

    @subject_slot("output_meter_level")
    def _output_meter_level_listener(self):
        # type: () -> None
        if not Config.TRACK_VOLUME_MONITORING:
            return
        if self._track.output_meter_level > Config.CLIPPING_TRACK_VOLUME:
            # some clicks e.g. when starting / stopping the song have this value
            if round(self._track.output_meter_level, 3) == 0.921:
                return
            Backend.client().show_warning(
                "%s is clipping (%.3f)" % (self.abstract_track.name, self._track.output_meter_level)
            )

    @property
    def current_monitoring_state(self):
        # type: () -> CurrentMonitoringStateEnum
        if self._track is None:
            return CurrentMonitoringStateEnum.AUTO
        return CurrentMonitoringStateEnum.from_value(self._track.current_monitoring_state)

    @current_monitoring_state.setter
    def current_monitoring_state(self, monitoring_state):
        # type: (CurrentMonitoringStateEnum) -> None
        try:
            self._track.current_monitoring_state = monitoring_state.value  # noqa
        except Exception as e:
            Backend.client().show_warning(str(e))

    @property
    def output_meter_left(self):
        # type: () -> float
        return self._track.output_meter_left if self._track else 0

    @property
    def instrument(self):
        # type: () -> Optional[InstrumentInterface]
        return self._instrument

    @instrument.setter
    def instrument(self, instrument):
        # type: (Optional[InstrumentInterface]) -> None
        self._instrument = instrument
        self.appearance.set_instrument(instrument)
        self._clip_slots.set_instrument(instrument)

    @property
    def instrument_track(self):
        # type: () -> SimpleTrack
        assert self.instrument, "track has not instrument"
        return self.base_track

    @property
    def is_foldable(self):
        # type: () -> bool
        return self._track and self._track.is_foldable

    @property
    def is_folded(self):
        # type: () -> bool
        return bool(self._track.fold_state) if self.is_foldable and self._track else True

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if not is_folded:
            for group_track in self.group_tracks:
                group_track.base_track.is_folded = False
        if self._track and self.is_foldable:
            self._track.fold_state = int(is_folded)

    @property
    def is_triggered(self):
        # type: () -> bool
        return any(clip_slot.is_triggered for clip_slot in self.clip_slots)

    @property
    def volume(self):
        # type: () -> float
        volume = self._track.mixer_device.volume.value if self._track else 0
        return volume_to_db(volume)

    @volume.setter
    def volume(self, volume):
        # type: (float) -> None
        volume = db_to_volume(volume)
        if self._track:
            Scheduler.defer(
                partial(
                    DeviceParameter.set_live_device_parameter,
                    self._track.mixer_device.volume,
                    volume,
                )
            )

    @property
    def color(self):
        # type: () -> int
        return self.appearance.color

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.appearance.color = color_index
        self._clip_config.color = color_index

        for clip in self.clips:
            clip.color = color_index

    def fire(self, scene_index):
        # type: (int) -> None
        clip = self.clip_slots[scene_index].clip
        if clip is not None:
            clip.fire()

    def stop(self, scene_index=None, next_scene_index=None, immediate=False):
        # type: (Optional[int], Optional[int], bool) -> None
        if scene_index is None:
            self._track.stop_all_clips(not immediate)  # noqa
            return

        # let tail play
        clip = self.clip_slots[scene_index].clip

        if clip is not None and clip.is_playing:
            clip.stop(wait_until_end=True)

    def delete(self):
        # type: () -> Sequence
        DomainEventBus.emit(SimpleTrackDeletedEvent(self))
        return Sequence().wait_for_event(TracksMappedEvent).done()

    def get_automated_parameters(self, scene_index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        if len(self.clip_slots) < scene_index + 1:
            return {}

        clip = self.clip_slots[scene_index].clip
        if clip is None:
            return {}

        return {
            param: self
            for param in clip.automation.get_automated_parameters(self.devices.parameters)
        }

    def scroll_volume(self, go_next):
        # type: (bool) -> None
        """Editing directly the mixer device volume"""
        volume = self._track.mixer_device.volume.value
        volume += 0.01 if go_next else -0.01
        volume = min(volume, 1)

        seq = Sequence()
        seq.defer()
        seq.add(
            partial(
                DeviceParameter.set_live_device_parameter,
                self._track.mixer_device.volume,
                volume,
            )
        )
        seq.add(lambda: StatusBar.show_message("Track volume: %.1f dB" % self.volume))
        seq.done()

    def reset_mixer(self):
        # type: () -> None
        self.volume = 0
        for param in self.devices.mixer_device.parameters:
            param.value = param.default_value

    def focus(self):
        # type: () -> Sequence
        # track can disappear out of view if this is done later
        track_color = self.color

        self.color = ColorEnum.FOCUSED.value

        seq = Sequence()

        if not ApplicationView.is_browser_visible():
            ApplicationView.show_browser()
            seq.defer()

            # trick
            if Song.selected_track() == self.base_track:
                seq.add(next(Song.simple_tracks()).select)

        seq.add(self.select)
        seq.defer()

        # defensive : this will normally be done before
        seq.add(lambda: Scheduler.wait_ms(2000, partial(setattr, self, "color", track_color)))

        return seq.done()

    def click(self):
        # type: () -> Sequence
        track_color = self.color

        seq = Sequence()
        seq.add(self.focus)
        seq.add(Backend.client().click_focused_track)
        seq.wait_for_backend_event("track_clicked", timeout=3000)
        seq.add(partial(setattr, self, "color", track_color))

        return seq.done()

    def save(self):
        # type: () -> Sequence
        track_color = self.color

        seq = Sequence()
        seq.add(partial(DomainEventBus.emit, SimpleTrackSaveStartedEvent()))
        seq.add(self.focus)
        seq.add(Backend.client().save_track_to_sub_tracks)
        seq.wait_for_backend_event("track_focused", timeout=3000)
        seq.add(partial(setattr, self, "color", track_color))
        seq.wait_for_backend_event("track_saved", timeout=10000)

        return seq.done()

    def flatten(self, flatten_track=True):
        # type: (bool) -> Sequence
        # this is needed to have flattened clip of the right length
        Song._live_song().stop_playing()

        clip_infos = ClipInfo.create_from_clips(self.clips, self.devices.parameters, True)

        for clip in self.clips:
            clip.loop.end = clip.loop.end_marker  # to have tails

        seq = Sequence()

        if flatten_track:
            recolor_track = partial(setattr, self, "color", self.color)
            seq.add(self.focus)
            seq.add(Backend.client().flatten_track)
            seq.wait_for_backend_event("track_focused")
            seq.add(recolor_track)
            seq.wait_for_backend_event("track_flattened")
            seq.defer()
        else:
            self.select()

        seq.add(partial(ClipInfo.restore_duplicate_clips, clip_infos))
        seq.add(partial(DomainEventBus.emit, SimpleTrackFlattenedEvent(clip_infos)))
        seq.defer()

        return seq.done()

    def isolate_clip_tail(self):
        # type: () -> Sequence
        clip = Song.selected_clip()
        assert clip.has_tail, "clip has no tail"
        assert len(self.clip_slots) > clip.index + 1, "No next clip slot"

        next_cs = self.clip_slots[clip.index + 1]
        assert next_cs.clip is None, "next clip slot has a clip"

        seq = Sequence()
        seq.add(partial(self.clip_slots[clip.index].duplicate_clip_to, next_cs))
        seq.add(clip.remove_tail)
        seq.add(lambda: next_cs.clip.crop_to_tail())
        seq.add(lambda: next_cs.clip.crop())

        return seq.done()

    @property
    def load_time(self):
        # type: () -> int
        return self.devices.load_time

    def disconnect(self):
        # type: () -> None
        super(SimpleTrack, self).disconnect()
        self.devices.disconnect()
        self._clip_slots.disconnect()
        if self.instrument:
            self.instrument.disconnect()
        if self.abstract_group_track and self.abstract_group_track.base_track == self:
            self.abstract_group_track.disconnect()
