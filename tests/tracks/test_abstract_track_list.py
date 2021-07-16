from protocol0.lom.track.AbstractTrackList import AbstractTrackList
from protocol0.tests.fixtures import make_song


def test_abstract_track_list():
    # type: () -> None
    song = make_song(count_simple_tracks=1)
    track_list = AbstractTrackList(song.simple_tracks)

    assert len(track_list) == 1
