from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.tests.fixtures import AbletonTrack
from a_protocol_0.tests.fixtures.simpleTrack import TrackType
from a_protocol_0.tests.test_all import p0
from a_protocol_0.sequence.Sequence import Sequence


def test_create_automation_group():
    with p0.component_guard():
        seq = Sequence()
        seq.add(p0.trackManager.group_track)
        # track = SimpleTrack(AbletonTrack(name="midi", track_type=TrackType.MIDI), 0)
        # p0.trackManager._added_track_listener()
        seq.done()
