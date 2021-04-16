from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.tests.fixtures import AbletonTrack
from a_protocol_0.tests.fixtures.simpleTrack import TrackType


def create_external_synth_track():
    midi_track = SimpleTrack(AbletonTrack(name="midi", track_type=TrackType.MIDI), 0)
