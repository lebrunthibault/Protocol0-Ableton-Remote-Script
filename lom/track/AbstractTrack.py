from abc import abstractproperty
from typing import Any, Optional, List
from typing import TYPE_CHECKING

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import TRACK_CATEGORIES, TRACK_CATEGORY_OTHER, EXTERNAL_SYNTH_NAMES
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin
from a_protocol_0.utils.utils import find_all_devices

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyDeprecation
class AbstractTrack(AbstractTrackActionMixin, AbstractControlSurfaceComponent):
    def __init__(self, track, index, *a, **k):
        # type: (Live.Track.Track, int, Any, Any) -> None
        self._track = track  # type: Live.Track.Track
        self._view = track.view  # type: Live.Track.Track.View
        super(AbstractTrack, self).__init__(name=self.name, *a, **k)
        self.is_foldable = self._track.is_foldable
        self.can_be_armed = self._track.can_be_armed
        self.index = index
        self.base_track = self  # type: SimpleTrack
        self.is_external_synth_track = self.name in EXTERNAL_SYNTH_NAMES
        self.is_simple_group = self.is_foldable and not self.is_external_synth_track
        self.selectable_track = self
        self.group_track = None  # type: Optional[SimpleTrack]
        self.group_tracks = []  # type: List[SimpleTrack]
        self.sub_tracks = []  # type: List[SimpleTrack]
        self.instrument = self.parent.deviceManager.create_instrument_from_simple_track(track=self)
        self.selected_recording_time = "4 bars"
        self.bar_count = 1
        self.is_midi = self._track.has_midi_input
        self.is_audio = self._track.has_audio_input
        self.base_color = Colors.get(self.name, default=self._track.color_index)

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
        return [device for track in self.all_tracks for device in find_all_devices(track._track)]

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
        # type: () -> Live.Device.Device
        self.base_track._track.delete_device(self.base_track.top_devices.index(device))

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track.is_visible

    @property
    def name(self):
        # type: () -> str
        return self._track.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self.name != name:
            self.parent.log_debug(name)
            self.parent.defer(lambda: setattr(self._track, "name", name))

    @property
    def is_automation(self):
        # type: () -> bool
        return "automation" in self.name.lower()

    @property
    def category(self):
        # type: () -> str
        for track_category in TRACK_CATEGORIES:
            if any([t for t in [self] + self.group_tracks if t.name.lower() == track_category.lower()]):
                return track_category

        return TRACK_CATEGORY_OTHER

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

    @abstractproperty
    def is_recording(self):
        # type: () -> bool
        pass

    @abstractproperty
    def arm(self):
        # type: () -> bool
        pass

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
