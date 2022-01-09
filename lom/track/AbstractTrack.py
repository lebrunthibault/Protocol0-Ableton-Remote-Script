from abc import abstractproperty
from functools import partial

from typing import Any, Optional, List, Type
from typing import TYPE_CHECKING

import Live
from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.ColorEnum import ColorEnum
from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.enums.Push2InstrumentModeEnum import Push2InstrumentModeEnum
from protocol0.enums.Push2MainModeEnum import Push2MainModeEnum
from protocol0.enums.Push2MatrixModeEnum import Push2MatrixModeEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.clip.Clip import Clip
from protocol0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin
from protocol0.lom.track.AbstractTrackName import AbstractTrackName
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot
from protocol0.utils.utils import set_device_parameter, find_if

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class AbstractTrack(AbstractTrackActionMixin, AbstractObject):
    __subject_events__ = ("is_recording", "devices")

    DEFAULT_NAME = "default"
    DEFAULT_COLOR = ColorEnum.DISABLED  # when the color cannot be matched
    KEEP_CLIPS_ON_ADDED = False

    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractTrack, self).__init__(*a, **k)
        # TRACKS
        self._track = track._track  # type: Live.Track.Track
        self.base_track = track  # type: SimpleTrack
        self.group_track = None  # type: Optional[AbstractTrack]
        # NB : .group_track is simple for simple tracks and abg for abg tracks
        self.abstract_group_track = None  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]

        if not self.base_track.IS_ACTIVE:
            return

        # MISC
        self.track_name = AbstractTrackName(self)  # type: AbstractTrackName

        self.protected_mode_active = True

        # PUSH2
        self.push2_selected_main_mode = Push2MainModeEnum.DEVICE
        self.push2_selected_matrix_mode = Push2MatrixModeEnum.SESSION
        self.push2_selected_instrument_mode = None  # type: Optional[Push2InstrumentModeEnum]

        # LISTENERS
        self._is_recording_listener.subject = self

    def __repr__(self):
        # type: () -> str
        return "P0 %s : %s (%s)" % (self.__class__.__name__, self.name, self.index + 1)

    def _added_track_init(self):
        # type: () -> Optional[Sequence]
        self.refresh_appearance()
        if self.KEEP_CLIPS_ON_ADDED:
            return None

        seq = Sequence()
        seq.add([clip.delete for clip in self.clips])
        return seq.done()

    def on_tracks_change(self):
        # type: () -> None
        pass

    def on_scenes_change(self):
        # type: () -> None
        pass

    @p0_subject_slot("is_recording")
    def _is_recording_listener(self):
        # type: () -> None
        self.solo = False
        if len(list(filter(None, [t.is_hearable for t in self.song.abstract_tracks]))) > 1:
            self.song.metronome = False

    @property
    def index(self):
        # type: () -> int
        return self.base_track._index

    @property
    def abstract_track(self):
        # type: () -> AbstractTrack
        """
        For lone tracks, will return self
        For group_tracks or sub_tracks of AbstractGroupTracks (except NormalGroupTrack)
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
    def instrument_class(self):
        # type: () -> Optional[Type[AbstractInstrument]]
        if self.instrument:
            return self.instrument.__class__
        else:
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
    def computed_base_name(self):
        # type: () -> str
        if self.instrument and self.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME:
            if self.instrument.selected_preset:
                return self.instrument.selected_preset.name
            else:
                return self.instrument.name
        elif self.instrument and self.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            return self.instrument._preset_list.selected_category
        else:
            return self.DEFAULT_NAME

    @property
    def color(self):
        # type: (AbstractTrack) -> int
        if self._track:
            return self._track.color_index
        else:
            return ColorEnum.DISABLED.index

    @color.setter
    def color(self, color_index):
        # type: (AbstractTrack, int) -> None
        if self._track and color_index != self._track.color_index:
            self._track.color_index = color_index

    @property
    def computed_color(self):
        # type: () -> int
        if self.is_foldable:
            sub_track_colors = [sub_track.color for sub_track in self.sub_tracks]
            if len(set(sub_track_colors)) == 1:
                return sub_track_colors[0]

        instrument = self.instrument or self.abstract_track.instrument
        if instrument:
            return instrument.TRACK_COLOR.index
        else:
            return self.DEFAULT_COLOR.index

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
        if self.is_foldable and self._track:
            self._track.fold_state = int(is_folded)

    @property
    def solo(self):
        # type: () -> bool
        return self._track and self._track.solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        if self._track:
            self._track.solo = solo

    @property
    def is_armed(self):
        # type: () -> bool
        return False

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        for track in self.active_tracks:
            track.is_armed = is_armed

    @property
    def has_monitor_in(self):
        # type: () -> bool
        return not self.is_foldable and self.base_track.current_monitoring_state == CurrentMonitoringStateEnum.IN

    @has_monitor_in.setter
    def has_monitor_in(self, has_monitor_in):
        # type: (bool) -> None
        try:
            if has_monitor_in:
                self.base_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
            else:
                self.base_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        except RuntimeError:
            pass  # Live throws sometimes 'Master or sendtracks have no monitoring state!'

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip_slot.clip for clip_slot in self.base_track.clip_slots if clip_slot.has_clip and clip_slot.clip]

    # noinspection PyDeprecation
    @abstractproperty
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        raise NotImplementedError

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track and self._track.is_visible

    @property
    def search_keywords(self):
        # type: () -> List[str]
        keywords = [self.name]
        if self.instrument:
            keywords += [self.instrument.name, self.instrument.preset_name]
            if self.instrument.selected_preset:
                keywords += [self.instrument.selected_preset.name]
        unique_keywords = list(set(" ".join(keywords).lower().split(" ")))
        return [kw for kw in unique_keywords if len(kw) >= 3]

    @property
    def is_playing(self):
        # type: () -> bool
        return self.base_track.is_playing or any(sub_track.is_playing for sub_track in self.sub_tracks)

    @property
    def is_record_triggered(self):
        # type: () -> bool
        return self.base_track.fired_slot_index >= 0 or any(clip for clip in self.clips if clip.is_recording) or any(
            sub_track for sub_track in self.sub_tracks if sub_track.is_record_triggered)

    @property
    def mute(self):
        # type: () -> bool
        return self._track and self._track.mute

    @mute.setter
    def mute(self, mute):
        # type: (bool) -> None
        if self._track:
            self._track.mute = mute

    @property
    def is_hearable(self):
        # type: () -> bool
        return (
                self.is_playing
                and self.output_meter_level > 0.2
                and (not self.abstract_group_track or self.abstract_group_track.is_hearable)
        )

    @property
    def is_recording(self):
        # type: () -> bool
        return False

    @property
    def can_be_armed(self):
        # type: () -> bool
        return self._track and self._track.can_be_armed

    @property
    def output_meter_level(self):
        # type: () -> float
        return self._track.output_meter_level if self._track else 0

    @output_meter_level.setter
    def output_meter_level(self, output_meter_level):
        # type: (float) -> None
        if self._track:
            self._track.output_meter_level = output_meter_level

    @property
    def volume(self):
        # type: () -> float
        return self._track.mixer_device.volume.value if self._track else 0

    @volume.setter
    def volume(self, volume):
        # type: (float) -> None
        if self._track:
            self.parent.defer(partial(set_device_parameter, self._track.mixer_device.volume, volume))

    @property
    def has_audio_output(self):
        # type: () -> bool
        return self._track and self._track.has_audio_output

    @property
    def available_input_routing_types(self):
        # type: () -> List[Live.Track.RoutingType]
        if self._track:
            return list(self._track.available_input_routing_types)
        else:
            return []

    @property
    def input_routing_track(self):
        # type: () -> Optional[SimpleTrack]
        if self._track and self._track.input_routing_type.attached_object:
            return self.parent.songTracksManager.get_simple_track(self._track.input_routing_type.attached_object)
        else:
            return None

    @input_routing_track.setter
    def input_routing_track(self, track):
        # type: (Optional[SimpleTrack]) -> None
        if self._track is None:
            return
        if track is None:
            input_routing_type = self.available_input_routing_types[-1]
        else:
            input_routing_type = find_if(lambda r: r.attached_object == track._track,
                                         self.available_input_routing_types)

        if not input_routing_type:
            raise Protocol0Error("Couldn't find the output routing type %s for %s" % (track, self))

        self._track.input_routing_type = input_routing_type

    @property
    def input_routing_type(self):
        # type: () -> Optional[InputRoutingTypeEnum]
        try:
            return self._track and InputRoutingTypeEnum.from_value(self._track.input_routing_type.display_name)
        except Protocol0Error:
            return None

    @input_routing_type.setter
    def input_routing_type(self, input_routing_type_enum):
        # type: (InputRoutingTypeEnum) -> None
        if self._track is None:
            return
        input_routing_type = find_if(lambda i: i.display_name == input_routing_type_enum.label,
                                     self.available_input_routing_types)
        if input_routing_type is None:
            raise Protocol0Error("Couldn't find input routing type from %s for %s" % (input_routing_type_enum, self))
        self._track.input_routing_type = input_routing_type

    @property
    def available_input_routing_channels(self):
        # type: () -> List[Live.Track.RoutingChannel]
        return self._track and list(self._track.available_input_routing_channels)

    @property
    def input_routing_channel(self):
        # type: () -> Optional[InputRoutingChannelEnum]
        try:
            return self._track and InputRoutingChannelEnum.from_value(self._track.input_routing_channel.display_name)
        except Protocol0Error:
            return None

    @input_routing_channel.setter
    def input_routing_channel(self, input_routing_channel):
        # type: (InputRoutingChannelEnum) -> None
        if self._track is None:
            return
        channel = find_if(lambda r: r.display_name == input_routing_channel.label,
                          self.available_input_routing_channels)
        if not channel:
            raise Protocol0Error("couldn't find channel matching %s for %s" % (input_routing_channel, self))
        self._track.input_routing_channel = channel

    @property
    def available_output_routing_types(self):
        # type: () -> List[Live.Track.RoutingType]
        if self._track:
            return list(self._track.available_output_routing_types)
        else:
            return []

    @property
    def output_routing_track(self):
        # type: () -> Optional[SimpleTrack]
        if self._track and self._track.output_routing_type.attached_object:
            return self.parent.songTracksManager.get_simple_track(self._track.output_routing_type.attached_object)
        elif self._track.output_routing_type.category == Live.Track.RoutingTypeCategory.parent_group_track:
            return self.group_track
        elif self._track.output_routing_type.category == Live.Track.RoutingTypeCategory.master:
            return self.song.master_track
        else:
            return None

    @output_routing_track.setter
    def output_routing_track(self, track):
        # type: (SimpleTrack) -> None
        if self._track is None:
            return
        output_routing_type = find_if(lambda r: r.attached_object == track._track, self.available_output_routing_types)

        if not output_routing_type:
            output_routing_type = find_if(lambda r: r.display_name == track.name, self.available_output_routing_types)

        if not output_routing_type:
            raise Protocol0Error("Couldn't find the output routing type %s for %s" % (track, self))

        self._track.output_routing_type = output_routing_type

    def disconnect(self):
        # type: () -> None
        super(AbstractTrack, self).disconnect()
        if hasattr(self, "track_name"):
            self.track_name.disconnect()
