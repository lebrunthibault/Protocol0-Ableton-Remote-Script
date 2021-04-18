from abc import abstractproperty
from functools import partial
from itertools import chain, imap

import Live
from typing import Any, Optional, List, Union
from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceChain import DeviceChain
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
    from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class AbstractTrack(AbstractTrackActionMixin, AbstractObject):
    __subject_events__ = ("instrument", "fired_slot_index")

    ADDED_TRACK_INIT_ENABLED = True

    def __init__(self, track, *a, **k):
        # type: (SimpleTrack) -> None
        super(AbstractTrack, self).__init__(*a, **k)
        self.index = track.index

        # TRACKS
        self._track = track._track
        self.base_track = track  # type: SimpleTrack
        self.group_track = self.parent.songManager._get_simple_track(self._track.group_track)
        # set in SongManager at track processing time
        self.abstract_group_track = None  # type: Optional[AbstractGroupTrack]
        # here this works because group tracks are at left of inner tracks (but for all_tracks we need a property)
        self.group_tracks = (
            [self.group_track] + self.group_track.group_tracks if self.group_track else []
        )  # type: List[SimpleTrack]
        self.sub_tracks = []  # type: List[SimpleTrack]

        self.track_name = TrackName(self)

        # DEVICES
        self._instrument = (
            None
        )  # type: Optional[AbstractInstrument]  #  None here so that we don't instantiate the same instrument twice
        self.instrument_track = self.base_track  # type: AbstractTrack
        self.devices = []  # type: List[Device]
        self.all_devices = []  # type: List[Device]
        self.all_visible_devices = []  # type: List[Device]
        self._devices_listener.subject = self._track
        self._devices_listener()

        # MISC
        self.is_foldable = self._track.is_foldable
        self._view = self._track.view  # type: Live.Track.Track.View
        self.is_scrollable = True
        self._is_hearable = True
        self._is_duplicated = False  # allows different init when duplicated or when created from e.g. the browser

        # DISPLAY
        self.nav_view = "track"
        self.push2_selected_main_mode = "device"
        self.push2_selected_matrix_mode = "session"
        self.push2_selected_instrument_mode = None

    def _added_track_init(self):
        """ this should be be called once, when the Live track is created, overridden by some child classes """
        if self.parent.songManager.abstract_group_track_creation_in_progress:
            return
        self.song.current_track.arm()
        self.song.current_track.stop()
        [setattr(track.track_name, "playing_slot_index", 0) for track in self.song.current_track.all_tracks]

        if not self._is_duplicated:
            self.set_device_parameter_value("Arpeggiator rack", "Chain Selector", 0)
            self.set_device_parameter_value("Serum rack", "Arp select", 0)
            if not self.has_device("Mix Rack"):
                self.load_any_device(DeviceType.RACK_DEVICE, "Mix Rack")

        seq = Sequence()
        [seq.add(clip.delete) for clip in self.song.current_track.all_clips]

        return seq.done()

    @property
    def name(self):
        # type: () -> str
        return self._track.name if self._track else ""

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._track and name:
            self._track.name = str(name).strip()

    @property
    def base_color(self):
        return (
            self.top_abstract_track.instrument.TRACK_COLOR
            if self.top_abstract_track.instrument
            else self._track.color_index
        )

    @property
    def instrument(self):
        # type: () -> AbstractInstrument
        return self._instrument

    @instrument.setter
    def instrument(self, instrument):
        # type: (AbstractInstrument) -> None
        self._instrument = instrument
        # noinspection PyUnresolvedReferences
        self.notify_instrument()

    def is_parent(self, track):
        # type: (AbstractTrack) -> bool
        return track in self.all_tracks

    @property
    def top_abstract_track(self):
        # type: () -> AbstractTrack
        top_abstract_track = self
        while top_abstract_track.abstract_group_track:
            top_abstract_track = top_abstract_track.abstract_group_track
        return top_abstract_track

    @property
    def all_tracks(self):
        # type: () -> List[SimpleTrack]
        all_tracks = [self.base_track]
        [all_tracks.extend(sub_track.all_tracks) for sub_track in self.sub_tracks]
        return all_tracks

    @property
    def all_clips(self):
        # type: () -> List[Clip]
        clip_slots = [clip_slot for track in self.all_tracks for clip_slot in track.clip_slots]
        return [clip_slot.clip for clip_slot in clip_slots if clip_slot.has_clip]

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip_slot.clip for clip_slot in self.base_track.clip_slots if clip_slot.has_clip]

    @abstractproperty
    def next_empty_clip_slot_index(self):
        raise NotImplementedError

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track.is_visible

    @property
    def category(self):
        # type: () -> TrackCategoryEnum
        for track_category in TrackCategoryEnum:
            if any(t for t in [self] + self.group_tracks if track_category.value.lower() in t.name):
                return track_category

        return TrackCategoryEnum.OTHER

    @property
    def base_name(self):
        # type: () -> str
        return self.base_track.track_name.base_name

    @property
    def selected_preset_index(self):
        # type: () -> int
        return self.base_track.track_name.selected_preset_index

    @property
    def color(self):
        # type: () -> int
        return self._track.color_index

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        for track in self.all_tracks:
            track._track.color_index = color_index

    @property
    def is_selected(self):
        self.song.selected_track in self.all_tracks

    @property
    def is_folded(self):
        # type: () -> bool
        return self._track.fold_state if self.is_foldable else False

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if self.is_foldable:
            self._track.fold_state = int(is_folded)

    @subject_slot("devices")
    def _devices_listener(self):
        [device.disconnect() for device in self.devices]
        self.devices = [Device.make(device, self.base_track, index) for index, device in enumerate(self._track.devices)]
        self.all_devices = self._find_all_devices(self.base_track)
        self.all_visible_devices = self._find_all_devices(self.base_track, only_visible=True)

        # here we need to refresh the instrument so that it doesn't point to an outdated device
        self.instrument_track.instrument = self.parent.deviceManager.make_instrument_from_simple_track(track=self)

    def get_device(self, device):
        # type: (Live.Device.Device) -> Optional[Device]
        return find_if(lambda d: d._device == device, self.base_track.all_devices)

    def has_device(self, device_name):
        return find_if(lambda d: d.name == device_name, self.base_track.all_devices)

    @property
    def selected_device(self):
        # type: () -> Device
        return self.get_device(self._track.view.selected_device)

    def delete_device(self, device):
        # type: (Device) -> None
        try:
            device.disconnect()
            self.base_track._track.delete_device(self.base_track.devices.index(device))
            self._devices_listener()  # this should be called by Live
        except Exception:
            pass

    def clear_devices(self):
        for device in self.devices:
            self.delete_device(self.devices[0])

    def _find_all_devices(self, track_or_chain, only_visible=False):
        # type: (Union[SimpleTrack, DeviceChain]) -> List[Device]
        u""" Returns a list with all devices from a track or chain """
        devices = []
        for device in filter(None, track_or_chain.devices):  # type: Device
            if not isinstance(device, RackDevice):
                devices += [device]
                continue

            if device.can_have_drum_pads and device.can_have_chains and device._view.is_showing_chain_devices:
                devices += chain([device], self._find_all_devices(device.selected_chain))
            elif not device.can_have_drum_pads and isinstance(device, RackDevice):
                devices += chain(
                    [device],
                    *imap(
                        partial(self._find_all_devices, only_visible=only_visible),
                        filter(None, device.chains),
                    )
                )
        return devices

    def all_devices(self, track_or_chain):
        devices = self.devices
        for device in [d for d in devices if isinstance(d, RackDevice)]:
            devices += self.all_devices(device.chains[0])
        return devices

    @property
    def device_parameters(self):
        # type: () -> List[DeviceParameter]
        return list(chain(*[device.parameters for device in self.all_devices]))

    def set_device_parameter_value(self, device_name, parameter_name, value, raise_if_not_exists=False):
        # type: (str, str, Any) -> Optional[Sequence]
        device = find_if(lambda d: d.name.lower() == device_name.lower(), self.song.current_track.all_devices)
        if not device:
            if not raise_if_not_exists:
                return
            raise Protocol0Error("Couldn't find device %s in track devices" % device_name)

        param = find_if(lambda d: d.name.lower() == parameter_name.lower(), device.parameters)

        if not param:
            if not raise_if_not_exists:
                return
            raise Protocol0Error("Couldn't find parameter %s in device %s" % (parameter_name, device_name))

        if param.is_enabled:
            seq = Sequence().add(wait=1)
            seq.add(lambda: setattr(param, "value", value))
            return seq.done()

    @property
    def is_playing(self):
        # type: () -> bool
        return any(simple_track.is_playing for simple_track in self.all_tracks)

    @property
    def mute(self):
        # type: () -> bool
        return self._track.mute

    @mute.setter
    def mute(self, mute):
        # type: (bool) -> None
        self._track.mute = mute

    @property
    def solo(self):
        # type: () -> bool
        return self._track.solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        self._track.solo = solo

    @property
    def has_monitor_in(self):
        # type: () -> bool
        return self._track.current_monitoring_state == 0

    @has_monitor_in.setter
    def has_monitor_in(self, has_monitor_in):
        # type: (bool) -> None
        self._track.current_monitoring_state = int(not has_monitor_in)

    @property
    def is_hearable(self):
        # type: () -> bool
        return (
            self._is_hearable
            and self.is_playing
            and self.output_meter_level > 0.5
            and not self.mute
            and all([not t.mute for t in self.group_tracks])
        )

    @property
    def is_recording(self):
        # type: () -> bool
        return False

    @property
    def can_be_armed(self):
        return self._track.can_be_armed

    @property
    def is_armed(self):
        # type: () -> bool
        return False

    @property
    def output_meter_level(self):
        # type: () -> float
        return self._track.output_meter_level

    @property
    def volume(self):
        # type: () -> float
        return self._track.mixer_device.volume.value

    @volume.setter
    @defer
    def volume(self, volume):
        # type: (float) -> None
        self._track.mixer_device.volume.value = volume

    @property
    def has_audio_output(self):
        # type: () -> bool
        return self._track.has_audio_output

    @property
    def available_output_routing_types(self):
        # type: () -> List[Live.Track.RoutingType]
        return list(self._track.available_output_routing_types)

    @property
    def available_input_routing_types(self):
        # type: () -> List[Live.Track.RoutingType]
        return list(self._track.available_input_routing_types)

    @property
    def output_routing_type(self):
        # type: () -> Live.Track.RoutingType
        return self._track.output_routing_type

    @output_routing_type.setter
    def output_routing_type(self, output_routing_type):
        # type: (Live.Track.RoutingType) -> None
        self._track.output_routing_type = output_routing_type

    @property
    def input_routing_type(self):
        # type: () -> Live.Track.RoutingType
        return self._track.input_routing_type

    @input_routing_type.setter
    def input_routing_type(self, input_routing_type):
        # type: (Live.Track.RoutingType) -> None
        self._track.input_routing_type = input_routing_type

    @property
    def current_input_routing(self):
        # type: () -> str
        return self._track.current_input_routing

    @current_input_routing.setter
    def current_input_routing(self, current_input_routing):
        # type: (str) -> None
        self._track.current_input_routing = current_input_routing

    @property
    def available_output_routing_channels(self):
        # type: () -> List[Live.Track.RoutingChannel]
        return list(self._track.available_output_routing_channels)

    @property
    def output_routing_channel(self):
        # type: () -> Live.Track.RoutingChannel
        return self._track.output_routing_channel

    @output_routing_channel.setter
    def output_routing_channel(self, output_routing_channel):
        # type: (Live.Track.RoutingChannel) -> None
        self._track.output_routing_channel = output_routing_channel

    def disconnect(self):
        super(AbstractTrack, self).disconnect()
        [device.disconnect() for device in self.devices]
        self.track_name.disconnect()
