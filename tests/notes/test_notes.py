from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.tests.fixtures.clip import AbletonClip
from a_protocol_0.tests.fixtures.clip_slot import AbletonClipSlot
from a_protocol_0.tests.fixtures.simpleTrack import AbletonTrack, TrackType


def create_clip_with_notes(notes, prev_notes=[], clip_length=None, loop_start=None, name="test"):
    # noinspection PyTypeChecker
    track = SimpleTrack(AbletonTrack(name="midi", track_type=TrackType.MIDI), 0)
    loop_start = loop_start if loop_start is not None else notes[0].start
    length = clip_length or notes[-1].end - loop_start
    # noinspection PyTypeChecker
    cs = ClipSlot(
        clip_slot=AbletonClipSlot(AbletonClip(length=length, name=name, loop_start=loop_start)),
        index=0,
        track=track,
    )
    clip = AutomationMidiClip(clip_slot=cs)
    clip._prev_notes = Note.copy_notes(prev_notes)
    for note in notes:
        note.clip = clip
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


def test_map_notes_loop_start_change():
    prev_notes = [
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes[1].pitch = 50

    (clip, res) = create_clip_with_notes(notes=notes, prev_notes=prev_notes)
    clip._map_notes()
    assert len(clip._prev_notes) == 3
    assert clip._prev_notes[0].start == 1
    assert clip._prev_notes[-1].start == 3
    for note in clip._prev_notes:
        assert note.duration == 1


def test_map_notes_loop_start_change_edit_last_note():
    prev_notes = [
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes[-1].pitch = 50

    (clip, res) = create_clip_with_notes(notes=notes, prev_notes=prev_notes)
    clip._map_notes(notes)
    assert len(clip._prev_notes) == 3
    assert clip._prev_notes[0].start == 1
    assert clip._prev_notes[-1].start == 3
    for note in clip._prev_notes:
        assert note.duration == 1
    assert clip._prev_notes[-1].velocity == 50


def test_add_missing_notes():
    prev_notes = [
        Note(start=0, duration=1, pitch=100, velocity=100),
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes.pop(1)

    (clip, res) = create_clip_with_notes(notes=notes, prev_notes=prev_notes)
    notes = list(clip._add_missing_notes(notes))

    assert len(clip._prev_notes) == 4
    assert clip._prev_notes[0].start == 0
    for note in clip._prev_notes:
        assert note.duration == 1


def test_add_missing_notes_loop_start_change():
    prev_notes = [
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes.pop(1)

    (clip, res) = create_clip_with_notes(notes=notes, prev_notes=prev_notes, loop_start=1)
    notes = list(clip._add_missing_notes(notes))

    assert len(clip._prev_notes) == 3
    assert clip._prev_notes[0].start == 1
    assert clip._prev_notes[-1].start == 3
    for note in clip._prev_notes:
        assert note.duration == 1


def test_consolidate_notes_2():
    notes = [
        Note(start=0, duration=4, pitch=127, velocity=127),
    ]
    (clip, res) = create_clip_with_notes(notes, notes)

    notes.append(Note(start=1, duration=1, pitch=126, velocity=126))
    clip._map_notes(notes)
    notes = Note.copy_notes(clip._prev_notes)
    notes.append(Note(start=0, duration=1, pitch=126, velocity=126))
    clip._map_notes(notes)


def test_consolidate_notes_3():
    notes = [
        Note(start=0, duration=2, pitch=0, velocity=0),
        Note(start=2, duration=2, pitch=127, velocity=127),
    ]
    (clip, res) = create_clip_with_notes(notes, notes)

    notes.append(Note(start=1, duration=0.25, pitch=80, velocity=80))
    clip._map_notes(notes)


#
# def test_ramp_notes():
#     notes = [
#         Note(start=0, duration=2, pitch=80, velocity=80),
#         Note(start=2, duration=2, pitch=100, velocity=100),
#     ]
#     (clip, res) = create_clip_with_notes(notes, prev_notes=notes)
#
#     def check_notes(notes, expected_count):
#         assert len(notes) == expected_count
#         assert notes[0].start == 0
#         assert notes[0].duration < 2
#         assert notes[3].velocity != notes[-1].velocity
#
#     check_notes(AutomationCurveGenerator.automation_notes(clip), 40)
#
#     # change note velocity
#     clip._prev_notes[1].velocity = 90
#     check_notes(AutomationCurveGenerator.automation_notes(clip), 20)


def test_add_note():
    notes = [
        Note(start=0, duration=1, pitch=0, velocity=0),
        Note(start=1, duration=3, pitch=100, velocity=100),
    ]
    (clip, res) = create_clip_with_notes(notes)

    clip._map_notes(notes)
    notes = Note.copy_notes(clip._prev_notes)
    # adding a note on at 1.1
    notes.append(Note(start=1, duration=0.25, pitch=50, velocity=90))
    notes.sort(key=lambda x: x.start)
    clip._map_notes(notes)
    assert_note(clip._prev_notes[1], {"start": 1, "duration": 0.25, "pitch": 50, "velocity": 50})
    assert_note(clip._prev_notes[2], {"start": 1.25, "pitch": 100, "velocity": 100})
    # adding another note at 1.2
    notes.append(Note(start=1.25, duration=0.25, pitch=95, velocity=50))
    clip._map_notes(notes)
    assert_note(clip._prev_notes[2], {"start": 1.25, "pitch": 95, "velocity": 95})


def test_modify_note_pitch():
    prev_notes = [
        Note(start=0, duration=2, pitch=80, velocity=80),
        Note(start=2, duration=2, pitch=100, velocity=100),
    ]

    def check_res(clip, res):
        assert len(res["set_notes"]) == 1
        assert len(clip._prev_notes) == 2
        assert res["set_notes"][0].pitch == 70
        assert clip._prev_notes[0].pitch == 70
        assert res["set_notes"][0].velocity == 70
        assert clip._prev_notes[0].velocity == 70

    notes = Note.copy_notes(prev_notes)
    notes[0].pitch = 70
    (clip, res) = create_clip_with_notes(notes, prev_notes)
    clip._map_notes(notes)
    check_res(clip, res)


def test_modify_note_velocity():
    prev_notes = [
        Note(start=0, duration=2, pitch=80, velocity=80),
        Note(start=2, duration=2, pitch=100, velocity=100),
    ]

    def check_res(clip, res):
        assert len(res["set_notes"]) == 1
        assert len(clip._prev_notes) == 2
        assert res["set_notes"][0].pitch == 70
        assert clip._prev_notes[0].pitch == 70
        assert res["set_notes"][0].velocity == 70
        assert clip._prev_notes[0].velocity == 70

    notes = Note.copy_notes(prev_notes)
    notes[0].velocity = 70
    (clip, res) = create_clip_with_notes(notes, prev_notes)
    clip._map_notes(notes)
    check_res(clip, res)


# def test_clean_duplicate_notes():
#     notes = [
#         Note(start=0, duration=2, pitch=80, velocity=80),
#         Note(start=0, duration=4, pitch=100, velocity=100),
#     ]
#
#     (clip, res) = create_clip_with_notes(notes)
#
#     notes = list(clip._remove_start_short_notes(notes))
#     assert len(notes) == 1
#     assert notes[0].duration == 4


def test_insert_min_note():
    notes = [
        Note(start=2, duration=2, pitch=100, velocity=100),
    ]

    (clip, res) = create_clip_with_notes(notes, loop_start=0)
    clip._map_notes(notes)
    assert_note(clip._prev_notes[0], {"start": 0, "duration": 2, "pitch": 0, "velocity": 0})
