from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.tests.fixtures.clip import AbletonClip
from a_protocol_0.tests.fixtures.clip_slot import AbletonClipSlot
from a_protocol_0.lom.Note import Note
from a_protocol_0.tests.fixtures.simpleTrack import AbletonTrack, TrackType
from a_protocol_0.tests.test_all import p0


def test_notes():
    notes = [
        Note(start=0, duration=1, pitch=100, velocity=100),
        Note(start=1, duration=1, pitch=100, velocity=100),
    ]

    with p0.component_guard():
        clip_duration = 4
        track = SimpleTrack(AbletonTrack(name="midi", track_type=TrackType.MIDI), 0)
        cs = ClipSlot(clip_slot=AbletonClipSlot(AbletonClip(clip_duration)), index=0, track=track)
        clip = AutomationMidiClip(clip_slot=cs)
        clip.get_notes = lambda: notes
        clip._map_notes = clip._map_notes.func
        res = {"notes": []}

        def replace_all_notes(notes):
            res["notes"] = notes
        clip.replace_all_notes = replace_all_notes

        clip._map_notes(clip)
        assert len(res["notes"]) == 1
        assert res["notes"][0].start == 0
        assert res["notes"][0].duration == clip_duration
