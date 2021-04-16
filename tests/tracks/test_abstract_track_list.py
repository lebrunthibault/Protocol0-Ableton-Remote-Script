from a_protocol_0.lom.track.AbstractTrackList import AbstractTrackList
from a_protocol_0.tests.fixtures.simpleTrack import make_midi_track
from a_protocol_0.tests.test_all import p0


def test_abstract_track_list():
    with p0.component_guard():
        midi_track = make_midi_track()
        track_list = AbstractTrackList([midi_track])

    assert len(track_list) == 1
