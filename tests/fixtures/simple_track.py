from typing import cast, List, Dict, Any

import Live
from _Framework.SubjectSlot import Subject
from protocol0.domain.lom.song.Song import Song


class TrackType(object):
    GROUP = "GROUP"
    MIDI = "MIDI"
    AUDIO = "AUDIO"


class AbletonTrack(Subject):
    __subject_events__ = ("name", "devices", "clip_slots", "playing_slot_index", "fired_slot_index", "color")

    def __init__(self, track_type=TrackType.MIDI):
        # type: (str, str) -> None
        self._live_ptr = id(self)
        self.name = track_type
        self.devices = []  # type: List[Live.Device.Device]
        self.can_be_armed = True
        self.is_armed = False
        self.fold_state = False
        self.is_visible = True
        self.has_midi_input = self.has_audio_output = self.is_foldable = self.fold_state = False
        self.clip_slots = []  # type: List[Live.ClipSlot.ClipSlot]
        self.view = None
        self.group_track = None
        self.color_index = 0
        self.has_audio_input = False
        self.has_audio_output = True
        self.has_midi_input = False

        self.track_type = track_type

        if track_type == TrackType.GROUP:
            self.is_foldable = True
            self.can_be_armed = False
            self.has_audio_input = True
        if track_type == TrackType.MIDI:
            self.has_midi_input = True
        if track_type == TrackType.AUDIO:
            self.has_audio_input = True

    def to_json(self):
        # type: () -> str
        return str(self)

    def get_data(self, _, __):
        # type: (str, Any) -> Dict
        return {}

    def __repr__(self):
        # type: () -> str
        return "%s - %s (%s)" % (self.__class__.__name__, self.track_type, self._live_ptr)


def add_track(song, track_type):
    # type: (Song, str) -> AbletonTrack
    live_track = AbletonTrack(track_type=track_type)
    song._song.tracks.append(cast(Live.Track.Track, live_track))
    return live_track


def add_external_synth_track(song, add_tail=False):
    # type: (Song, bool) -> AbletonTrack
    group_track = add_track(song, track_type=TrackType.GROUP)
    midi_track = add_track(song, track_type=TrackType.MIDI)
    audio_track = add_track(song, track_type=TrackType.AUDIO)
    midi_track.group_track = group_track
    audio_track.group_track = group_track

    if add_tail:
        audio_tail_track = add_track(song, track_type=TrackType.AUDIO)
        audio_tail_track.group_track = group_track
    return group_track
