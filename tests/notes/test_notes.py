from copy import copy
from functools import partial

from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.sequence.SequenceState import SequenceLogLevel
from a_protocol_0.tests.fixtures.clip import AbletonClip
from a_protocol_0.tests.fixtures.clip_slot import AbletonClipSlot
from a_protocol_0.lom.Note import Note
from a_protocol_0.tests.fixtures.simpleTrack import AbletonTrack, TrackType
# noinspection PyUnresolvedReferences
from a_protocol_0.tests.test_all import p0
from a_protocol_0.utils.log import log_ableton


def create_clip_with_notes(notes, prev_notes=[]):
    track = SimpleTrack(AbletonTrack(name="midi", track_type=TrackType.MIDI), 0)
    cs = ClipSlot(clip_slot=AbletonClipSlot(AbletonClip()), index=0, track=track)
    clip = AutomationMidiClip(clip_slot=cs)
    clip._prev_notes = prev_notes
    [setattr(note, "clip", clip) for note in notes]
    test_res = {"set_notes": []}
    clip.map_notes.__func__.wait_time = 0

    def replace_all_notes(notes):
        clip._prev_notes = notes

    def set_notes(notes):
        test_res["set_notes"] = notes

    clip.replace_all_notes = replace_all_notes
    clip.set_notes = set_notes

    return (clip, test_res)


def assert_note(note, expected):
    for key in expected.keys():
        assert getattr(note, key) == expected[key]


def test_consolidate_notes():
    notes = [
        Note(start=0, duration=1, pitch=100, velocity=100),
        Note(start=1, duration=1, pitch=100, velocity=100),
    ]
    (clip, res) = create_clip_with_notes(notes)

    clip._map_notes(notes)

    assert len(clip._prev_notes) == 1
    assert clip._prev_notes[0].start == 0
    assert clip._prev_notes[0].duration == clip.length


def test_ramp_notes():
    notes = [
        Note(start=0, duration=1, pitch=80, velocity=80),
        Note(start=1, duration=1, pitch=100, velocity=100),
    ]
    (clip, res) = create_clip_with_notes(notes)

    def check_res(clip, res):
        assert len(clip._prev_notes) == clip.ramping_steps + 1
        assert clip._prev_notes[0].start == 0
        assert clip._prev_notes[0].duration == 1

    seq = Sequence()
    clip._map_notes(notes)
    check_res(clip, res)
    notes = copy(clip._prev_notes)
    notes[1] = copy(notes[1])
    notes[1].velocity = 90
    clip._map_notes(notes)
    check_res(clip, res)
    assert clip._prev_notes[2].velocity <= clip._prev_notes[1].velocity
    seq.done()


def test_add_note():
    notes = [
        Note(start=0, duration=1, pitch=0, velocity=0),
        Note(start=1, duration=1, pitch=100, velocity=100),
    ]
    (clip, res) = create_clip_with_notes(notes)

    def check_res(clip, res):
        log_ableton(clip._prev_notes[0])
        log_ableton(clip._prev_notes[1])
        log_ableton(clip._prev_notes[2])
        # assert len(clip._prev_notes) == clip.ramping_steps + 1
        # assert clip._prev_notes[0].start == 0
        # assert clip._prev_notes[0].duration == 1

    seq = Sequence()
    clip._map_notes(notes)
    notes = copy(clip._prev_notes)
    # adding a note on the second beat
    notes.append(Note(start=1, duration=0.25, pitch=50, velocity=90))
    notes.sort(key=lambda x: x.start)
    clip._map_notes(notes)
    assert_note(clip._prev_notes[1], {"start": 1, "duration": 0.25, "pitch": 50, "velocity": 50})
    assert_note(clip._prev_notes[2], {"start": 1.25, "pitch": 100, "velocity": 100})
    notes.append(Note(start=1.25, duration=0.25, pitch=95, velocity=50))
    clip._map_notes(notes)
    check_res(clip, res)
    seq.done()


def test_modify_note_pitch():
    prev_notes = [
        Note(start=0, duration=1, pitch=80, velocity=80),
        Note(start=1, duration=1, pitch=100, velocity=100),
    ]

    def check_res(clip, res):
        assert len(res["set_notes"]) == 1
        assert len(clip._prev_notes) == clip.ramping_steps + 1
        assert res["set_notes"][0].pitch == 70
        assert clip._prev_notes[0].pitch == 70
        assert res["set_notes"][0].velocity == 70
        assert clip._prev_notes[0].velocity == 70

    seq = Sequence(log_level=SequenceLogLevel.disabled)

    # pitch change
    notes = [copy(note) for note in prev_notes]
    notes[0].pitch = 70
    (clip, res) = create_clip_with_notes(notes, prev_notes)
    seq.add(partial(clip._map_notes, notes))
    seq.add(partial(check_res, clip, res))

    return seq.done()


def test_modify_note_velocity():
    prev_notes = [
        Note(start=0, duration=1, pitch=80, velocity=80),
        Note(start=1, duration=1, pitch=100, velocity=100),
    ]

    def check_res(clip, res):
        assert len(res["set_notes"]) == 1
        assert len(clip._prev_notes) == clip.ramping_steps + 1
        assert res["set_notes"][0].pitch == 70
        assert clip._prev_notes[0].pitch == 70
        assert res["set_notes"][0].velocity == 70
        assert clip._prev_notes[0].velocity == 70

    seq = Sequence(log_level=SequenceLogLevel.disabled)

    # vel change
    notes = [copy(note) for note in prev_notes]
    notes[0].velocity = 70
    (clip, res) = create_clip_with_notes(notes, prev_notes)
    seq.add(partial(clip._map_notes, notes))
    seq.add(partial(check_res, clip, res))

    return seq.done()
