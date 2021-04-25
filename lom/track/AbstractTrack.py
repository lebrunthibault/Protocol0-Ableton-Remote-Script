from abc import abstractproperty

import Live
from typing import Any, Optional, List
from typing import TYPE_CHECKING

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.devices.InstrumentSimpler import InstrumentSimpler
from a_protocol_0.enums.Push2MainModeEnum import Push2MainModeEnum
from a_protocol_0.enums.Push2MatrixModeEnum import Push2MatrixModeEnum
from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
    from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class AbstractTrack(AbstractTrackActionMixin, AbstractObject):
    __subject_events__ = ("instrument", "fired_slot_index")

    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractTrack, self).__init__(*a, **k)
        # TRACKS
        self._track = track._track  # type: Live.Track.Track
        self.base_track = track  # type: SimpleTrack
        self.group_track = None  # type: Optional[AbstractTrack]
        self.abstract_group_track = None  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]

        # MISC
        self.track_name = TrackName(self)  # type: TrackName
        self.is_foldable = self._track.is_foldable  # type: bool

        # DISPLAY
        self.push2_selected_main_mode = Push2MainModeEnum.DEVICE
        self.push2_selected_matrix_mode = Push2MatrixModeEnum.SESSION
        self.push2_selected_instrument_mode = None  # type: Optional[str]

    def _added_track_init(self, arm=True):
        # type: (bool) -> Optional[Sequence]
        """ this should be be called once, when the Live track is created, overridden by some child classes """
        if arm:
            self.song.current_track.arm()
        self.song.current_track.stop()

        if not self.base_track.has_device("Mix Rack"):
            self.load_any_device(DeviceType.RACK_DEVICE, "Mix Rack")

        seq = Sequence()
        [seq.add(clip.delete) for clip in self.clips]

        return seq.done()

    @property
    def index(self):
        # type: () -> int
        return self.song.simple_tracks.index(self.base_track)

    @property
    def abstract_track(self):
        # type: () -> AbstractTrack
        """
        For lone tracks, will return self
        For group_tracks or sub_tracks of AbstractGroupTracks (except SimpleGroupTrack)
        will return the AbstractGroupTrack
        """
        return self.abstract_group_track if self.abstract_group_track else self  # type: ignore

    @property
    def active_tracks(self):
        # type: () -> List[AbstractTrack]
        raise NotImplementedError

    @property
    def instrument(self):
        # type: () -> Optional[AbstractInstrument]
        return None

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
        # type: () -> int
        return self.abstract_track.instrument.TRACK_COLOR if self.abstract_track.instrument else self._track.color_index

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip_slot.clip for clip_slot in self.base_track.clip_slots if clip_slot.has_clip]

    @abstractproperty
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        raise NotImplementedError

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track.is_visible

    @property
    def category(self):
        # type: () -> TrackCategoryEnum
        if self.instrument and isinstance(self.instrument, InstrumentSimpler):
            return TrackCategoryEnum.DRUMS
        for track_category in list(TrackCategoryEnum):
            if self.name in track_category.value.lower():
                return track_category

        if self.abstract_group_track:
            return self.abstract_group_track.category
        elif self.group_track:
            return self.group_track.category

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
    def is_playing(self):
        # type: () -> bool
        return any(track.is_playing for track in [self] + self.sub_tracks)

    @property
    def mute(self):
        # type: () -> bool
        return self._track.mute

    @mute.setter
    def mute(self, mute):
        # type: (bool) -> None
        self._track.mute = mute

    @property
    def is_hearable(self):
        # type: () -> bool
        return (
            self.is_playing
            and self.output_meter_level > 0.5
            and (not self.abstract_group_track or self.abstract_group_track.is_hearable)
        )

    @property
    def is_recording(self):
        # type: () -> bool
        return False

    @property
    def can_be_armed(self):
        # type: () -> bool
        return self._track.can_be_armed

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

    def disconnect(self):
        # type: () -> None
        super(AbstractTrack, self).disconnect()
        self.track_name.disconnect()
