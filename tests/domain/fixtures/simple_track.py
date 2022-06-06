from collections import namedtuple

import Live
from _Framework.SubjectSlot import Subject
from typing import cast, List

from protocol0.shared.SongFacade import SongFacade
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.device import AbletonDevice


class TrackType(object):
    GROUP = "GROUP"
    MIDI = "MIDI"
    AUDIO = "AUDIO"


class AbletonTrack(Subject):
    __subject_events__ = (
        "name",
        "solo",
        "devices",
        "clip_slots",
        "playing_slot_index",
        "fired_slot_index",
        "color",
        "output_meter_level"
    )

    def __init__(self, track_type=TrackType.MIDI):
        # type: (str, str) -> None
        self._live_ptr = id(self)
        self.name = track_type
        self.devices = []  # type: List[AbletonDevice]
        mixer_device = namedtuple('mixer_device', ['sends', 'volume',
                                                   'panning'])
        self.mixer_device = mixer_device([], 0, 0)
        self.arm = False
        self.solo = False
        self.fold_state = False
        self.is_visible = True
        self.has_midi_input = self.has_audio_output = self.is_foldable = self.fold_state = False
        self.available_input_routing_types = []
        self.available_input_routing_channels = []
        self.clip_slots = [AbletonClipSlot()]
        self.view = None
        self.group_track = None
        self.color_index = 0
        self.has_audio_input = False
        self.has_audio_output = True
        self.has_midi_input = False

        self.track_type = track_type

        if track_type == TrackType.GROUP:
            self.is_foldable = True
            self.has_audio_input = True
        if track_type == TrackType.MIDI:
            self.has_midi_input = True
        if track_type == TrackType.AUDIO:
            self.has_audio_input = True

    def __repr__(self):
        # type: () -> str
        return "%s - %s (%s)" % (self.__class__.__name__, self.track_type, self._live_ptr)


def add_track(track_type):
    # type: (str) -> AbletonTrack
    live_track = AbletonTrack(track_type=track_type)
    SongFacade._live_song().tracks.append(cast(Live.Track.Track, live_track))
    return live_track
