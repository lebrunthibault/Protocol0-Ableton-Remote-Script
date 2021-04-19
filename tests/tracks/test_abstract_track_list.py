from a_protocol_0.lom.track.AbstractTrackList import AbstractTrackList
from a_protocol_0.tests.fixtures import make_song
from a_protocol_0.tests.fixtures.simple_track import make_midi_track
from a_protocol_0.tests.test_all import p0


def test_abstract_track_list():
    # type: () -> None
    with p0.component_guard():
        midi_track = make_midi_track(make_song())
        track_list = AbstractTrackList([midi_track])

    assert len(track_list) == 1
