from abc import abstractproperty
from typing import Any, Optional, List
from typing import TYPE_CHECKING

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import TRACK_CATEGORIES, TRACK_CATEGORY_OTHER
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer
from a_protocol_0.utils.utils import find_all_devices

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


# noinspection PyDeprecation
class AbstractTrack(AbstractTrackActionMixin, AbstractControlSurfaceComponent):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        self._track = track._track
        self._view = self._track.view  # type: Live.Track.Track.View
        self.base_track = track  # type: SimpleTrack
        super(AbstractTrack, self).__init__(name=self.name, *a, **k)
        self.is_foldable = self._track.is_foldable
        self.can_be_armed = self._track.can_be_armed
        self.index = track.index
        self.is_simple_group = self.is_foldable and self not in self.parent.songManager._simple_track_to_abstract_group_track
        self.group_track = self.parent.songManager._get_simple_track(self._track.group_track) if self._track.group_track else None
        # here this works because group tracks are at left of inner tracks (but for all_tracks we need a property)
        self.group_tracks = [self.group_track] + self.group_track.group_tracks if self.group_track else []  # type: List[SimpleTrack]
        self.sub_tracks = []  # type: List[SimpleTrack]
        self.bar_count = 1
        self.is_midi = self._track.has_midi_input
        self.is_audio = self._track.has_audio_input
        self.base_color = Colors.get(self.name, default=self._track.color_index)
        self.instrument = None  # type: Optional[AbstractInstrument]  #  None here so that we don't instantiate the same instrument twice
        self.is_scrollable = True
        self.push2_selected_main_mode = 'device'
        self.push2_selected_matrix_mode = 'session'
        self.push2_selected_instrument_mode = None

    def _added_track_init(self):
        """ this should be be called once, when the Live track is created """
        self.song.current_track.action_arm()
        [clip.delete() for clip in self.song.current_track.all_clips]
        [setattr(TrackName(track), "clip_slot_index", 0) for track in self.song.current_track.all_tracks]
        arp = find_if(lambda d: d.name.lower() == "arpeggiator rack", self.song.current_track.all_devices)
        if arp:
            chain_selector_param = find_if(lambda d: d.name.lower() == "chain selector", arp.parameters)
            if chain_selector_param and chain_selector_param.is_enabled:
                chain_selector_param.value = 0

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
    def top_devices(self):
        # type: () -> List[Live.Device.Device]
        return list(self.base_track._track.devices)

    @property
    def all_devices(self):
        # type: () -> List[Live.Device.Device]
        return [device for track in self.all_tracks for device in find_all_devices(track)]

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip_slot.clip for clip_slot in self.base_track.clip_slots if clip_slot.has_clip]

    def get_clip_slot(self, clip_slot):
        # type: (Live.ClipSlot.ClipSlot) -> Optional[ClipSlot]
        return find_if(lambda cs: cs._clip_slot == clip_slot, self.base_track.clip_slots)

    def get_clip(self, clip):
        # type: (Live.Clip.Clip) -> Optional[Clip]
        return find_if(lambda c: c._clip == clip, self.base_track.clips)

    @property
    def selected_device(self):
        # type: () -> Live.Device.Device
        return self._track.view.selected_device

    def delete_device(self, device):
        # type: (Live.Device.Device) -> None
        self.base_track._track.delete_device(self.base_track.top_devices.index(device))

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track.is_visible

    @property
    def name(self):
        # type: () -> str
        return TrackName(self).name.lower()

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._track.name != name:
            try:
                self._track.name = name
            except RuntimeError:
                self.parent.defer(lambda: setattr(self._track, "name", name))

    @property
    def category(self):
        # type: () -> str
        for track_category in TRACK_CATEGORIES:
            if any([t for t in [self] + self.group_tracks if track_category.lower() in t.name]):
                return track_category

        return TRACK_CATEGORY_OTHER

    @property
    def preset_index(self):
        # type: () -> int
        return TrackName(self).preset_index

    @property
    def clip_slot_index(self):
        # type: () -> int
        return TrackName(self).clip_slot_index

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
    def is_folded(self):
        # type: () -> bool
        return self._track.fold_state if self.is_foldable else False

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if self.is_foldable:
            self._track.fold_state = int(is_folded)

    @abstractproperty
    def is_playing(self):
        # type: () -> bool
        pass

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
        return self.is_playing and self.output_meter_level > 0.5 and not self.mute and all([not t.mute for t in self.group_tracks])

    @abstractproperty
    def is_recording(self):
        # type: () -> bool
        pass

    @abstractproperty
    def arm(self):
        # type: () -> bool
        pass

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
    def output_routing_type(self):
        # type: () -> Live.Track.RoutingType
        return self._track.output_routing_type

    @output_routing_type.setter
    def output_routing_type(self, output_routing_type):
        # type: (Live.Track.RoutingType) -> None
        self._track.output_routing_type = output_routing_type

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
