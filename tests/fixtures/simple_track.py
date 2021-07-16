import Live
from typing import cast, List

from _Framework.SubjectSlot import Subject
from protocol0.lom.Song import Song
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class TrackType(object):
    GROUP = 1
    MIDI = 2
    AUDIO = 3


class AbletonTrack(Subject):
    __subject_events__ = ("name", "devices", "clip_slots", "playing_slot_index", "fired_slot_index", "color")

    def __init__(self, name="test_track", track_type=TrackType.MIDI):
        # type: (str, int) -> None
        self.name = name
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

        if track_type == TrackType.GROUP:
            self.is_foldable = True
            self.can_be_armed = False
        if track_type == TrackType.MIDI:
            self.has_midi_input = True
        if track_type == TrackType.AUDIO:
            self.has_audio_input = True


def make_simple_track(song, track_type):
    # type: (Song, int) -> SimpleTrack
    simple_track = SimpleTrack(cast(Live.Track.Track, AbletonTrack(track_type=TrackType.GROUP)))
    song.live_track_to_simple_track[simple_track._track] = simple_track
    return simple_track
