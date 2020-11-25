from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.tests.fixtures.device import AbletonDevice, make_device_simpler


class TrackType(object):
    GROUP = 1
    MIDI = 2
    AUDIO = 3


class AbletonTrack(object):
    def __init__(self, name="track", device=None, track_type=TrackType.MIDI):
        # type: (str, AbletonDevice, int) -> None
        self.name = name
        self.devices = [device] if device else []
        self.can_be_armed = True
        self.arm = False
        self.fold_state = False
        self.is_visible = True
        self.has_midi_input = self.has_audio_output = self.is_foldable = self.fold_state = False
        self.clip_slots = []

        if track_type == TrackType.GROUP:
            self.is_foldable = True
            self.can_be_armed = False
        if track_type == TrackType.MIDI:
            self.has_midi_input = True
        if track_type == TrackType.AUDIO:
            self.has_audio_output = True

    @staticmethod
    def name_has_listener(_):
        return True

    def add_name_listener(self, func):
        pass


def make_group_track(song, name=TrackName.GROUP_PROPHET_NAME):
    # type: (Song, str) -> SimpleTrack
    simple_track = SimpleTrack(song, AbletonTrack(name=name, track_type=TrackType.GROUP), len(song.tracks))
    song.tracks.append(simple_track)
    return simple_track


def make_midi_track(song, name="midi"):
    # type: (Song, str) -> SimpleTrack
    simple_track = SimpleTrack(song, AbletonTrack(name=name, track_type=TrackType.MIDI), len(song.tracks))
    song.tracks.append(simple_track)
    return simple_track


def make_audio_track(song, name="audio"):
    # type: (Song, str) -> SimpleTrack
    simple_track = SimpleTrack(song, AbletonTrack(name=name, track_type=TrackType.AUDIO), len(song.tracks))
    song.tracks.append(simple_track)
    return simple_track


def make_simpler_track(song, name="simpler"):
    # type: (Song, str) -> SimpleTrack
    simple_track = SimpleTrack(song, AbletonTrack(name=name, device=make_device_simpler()), len(song.tracks))
    song.tracks.append(simple_track)
    return simple_track