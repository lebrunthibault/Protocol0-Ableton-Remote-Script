from protocol0.lom.Song import Song
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.tests.fixtures.simple_track import make_simple_track


def make_external_synth_track(song):
    # type: (Song) -> ExternalSynthTrack
    track_group = make_simple_track(song)
    make_simple_track(song)
    make_simple_track(song)
    # noinspection PyTypeChecker
    return ExternalSynthTrack(song, track_group)
