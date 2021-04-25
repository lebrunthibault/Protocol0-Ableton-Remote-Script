from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.tests.fixtures.simple_track import make_simple_track, TrackType


def make_external_synth_track(song):
    # type: (Song) -> ExternalSynthTrack
    track_group = make_simple_track(song, track_type=TrackType.GROUP)
    make_simple_track(song, track_type=TrackType.MIDI)
    make_simple_track(song, track_type=TrackType.AUDIO)
    # noinspection PyTypeChecker
    return ExternalSynthTrack(song, track_group)
