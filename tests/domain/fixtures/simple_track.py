from collections import namedtuple

import Live
from _Framework.SubjectSlot import Subject
from typing import cast, List, Any

from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.device import AbletonDevice
from protocol0.tests.domain.fixtures.device_parameter import AbletonDeviceParameter


class TrackType(object):
    GROUP = "GROUP"
    MIDI = "MIDI"
    AUDIO = "AUDIO"


class TrackRoutingType(object):
    def __init__(self, display_name=""):
        # type: (str) -> None
        self.display_name = display_name
        self.attached_object = None
        self.category = Live.Track.RoutingTypeCategory.none


class AbletonTrack(Subject):
    __subject_events__ = (
        "name",
        "solo",
        "devices",
        "clip_slots",
        "playing_slot_index",
        "fired_slot_index",
        "color",
        "output_meter_level",
    )

    def __init__(self, track_type=TrackType.MIDI):
        # type: (str) -> None
        self._live_ptr = id(self)
        self.name = track_type
        self.devices = []  # type: List[AbletonDevice]
        mixer_device = namedtuple("mixer_device", ["sends", "volume", "panning"])
        self.mixer_device = mixer_device([], AbletonDeviceParameter("volume"), AbletonDeviceParameter("panning"))
        self.can_be_armed = True
        self.arm = False
        self.solo = False
        self.fold_state = False
        self.is_visible = True
        self.has_midi_input = self.is_foldable = self.fold_state = False
        self.available_input_routing_types = []
        self.available_input_routing_channels = []
        self.available_output_routing_types = [
            TrackRoutingType(OutputRoutingTypeEnum.SENDS_ONLY.label)
        ]
        self.output_routing_type = self.available_output_routing_types[0]
        self.clip_slots = [AbletonClipSlot()]
        self.view = None
        self.group_track = None
        self.color_index = 0
        self.has_audio_input = False
        self.has_midi_input = False

        self.track_type = track_type

        if track_type == TrackType.GROUP:
            self.is_foldable = True
            self.has_audio_input = True
        if track_type == TrackType.MIDI:
            self.has_midi_input = True
        if track_type == TrackType.AUDIO:
            self.has_audio_input = True

    def get_data(self, _, __):
        # type: (Any, Any) -> None
        pass

    def set_data(self, _, __):
        # type: (Any, Any) -> None
        pass

    def __repr__(self):
        # type: () -> str
        return "%s - %s" % (self.track_type, self.name)


def add_track(track_type):
    # type: (str) -> AbletonTrack
    live_track = AbletonTrack(track_type=track_type)
    Song._live_song().tracks.append(cast(Live.Track.Track, live_track))
    return live_track
