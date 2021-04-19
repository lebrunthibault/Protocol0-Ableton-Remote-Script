from typing import List, Dict

from a_protocol_0.automation.AutomationCurveGenerator import AutomationCurveGenerator
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.tests.fixtures.clip import create_automation_midi_clip_with_notes


def assert_note(note, expected):
    # type: (Note, Dict[str, float]) -> None
    for key in expected.keys():
        assert getattr(note, key) == expected[key]


def test_map_notes_loop_start_change():
    # type: () -> None
    prev_notes = [
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes[1].pitch = 50

    (clip, _) = create_automation_midi_clip_with_notes(notes=notes, prev_notes=prev_notes)
    clip._map_notes()
    assert len(clip._prev_notes) == 3
    assert clip._prev_notes[0].start == 1
    assert clip._prev_notes[-1].start == 3
    for note in clip._prev_notes:
        assert note.duration == 1


def test_map_notes_loop_start_change_edit_last_note():
    # type: () -> None
    prev_notes = [
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes[-1].pitch = 50

    (clip, _) = create_automation_midi_clip_with_notes(notes=notes, prev_notes=prev_notes)
    clip._map_notes(notes)
    assert len(clip._prev_notes) == 3
    assert clip._prev_notes[0].start == 1
    assert clip._prev_notes[-1].start == 3
    for note in clip._prev_notes:
        assert note.duration == 1
    assert clip._prev_notes[-1].velocity == 50


def test_add_missing_notes():
    # type: () -> None
    prev_notes = [
        Note(start=0, duration=1, pitch=100, velocity=100),
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes.pop(1)

    (clip, _) = create_automation_midi_clip_with_notes(notes=notes, prev_notes=prev_notes)
    notes = list(clip._add_missing_notes(notes))

    assert len(clip._prev_notes) == 4
    assert clip._prev_notes[0].start == 0
    for note in clip._prev_notes:
        assert note.duration == 1


def test_add_missing_notes_loop_start_change():
    # type: () -> None
    prev_notes = [
        Note(start=1, duration=1, pitch=80, velocity=80),
        Note(start=2, duration=1, pitch=60, velocity=60),
        Note(start=3, duration=1, pitch=40, velocity=40),
    ]

    notes = Note.copy_notes(prev_notes)
    notes.pop(1)

    (clip, _) = create_automation_midi_clip_with_notes(notes=notes, prev_notes=prev_notes, loop_start=1)
    notes = list(clip._add_missing_notes(notes))

    assert len(clip._prev_notes) == 3
    assert clip._prev_notes[0].start == 1
    assert clip._prev_notes[-1].start == 3
    for note in clip._prev_notes:
        assert note.duration == 1


def test_consolidate_notes_2():
    # type: () -> None
    notes = [
        Note(start=0, duration=4, pitch=127, velocity=127),
    ]
    (clip, _) = create_automation_midi_clip_with_notes(notes, notes)

    notes.append(Note(start=1, duration=1, pitch=126, velocity=126))
    clip._map_notes(notes)
    notes = Note.copy_notes(clip._prev_notes)
    notes.append(Note(start=0, duration=1, pitch=126, velocity=126))
    clip._map_notes(notes)


def test_consolidate_notes_3():
    # type: () -> None
    notes = [
        Note(start=0, duration=2, pitch=0, velocity=0),
        Note(start=2, duration=2, pitch=127, velocity=127),
    ]
    (clip, _) = create_automation_midi_clip_with_notes(notes, notes)

    notes.append(Note(start=1, duration=0.25, pitch=80, velocity=80))
    clip._map_notes(notes)


def test_ramp_notes():
    # type: () -> None

    notes = [
        Note(start=0, duration=2, pitch=80, velocity=80),
        Note(start=2, duration=2, pitch=100, velocity=100),
    ]
    (clip, _) = create_automation_midi_clip_with_notes(notes, prev_notes=notes)

    def check_notes(notes, expected_count):
        # type: (List[Note], int) -> None
        assert len(notes) == expected_count
        assert notes[0].start == 0
        assert notes[0].duration < 2
        assert notes[3].velocity != notes[-1].velocity

    check_notes(AutomationCurveGenerator.automation_notes(clip), 40)

    # change note velocity
    clip._prev_notes[1].velocity = 90
    check_notes(AutomationCurveGenerator.automation_notes(clip), 20)


def test_add_note():
    # type: () -> None
    notes = [
        Note(start=0, duration=1, pitch=0, velocity=0),
        Note(start=1, duration=3, pitch=100, velocity=100),
    ]
    (clip, _) = create_automation_midi_clip_with_notes(notes)

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
    # type: () -> None
    prev_notes = [
        Note(start=0, duration=2, pitch=80, velocity=80),
        Note(start=2, duration=2, pitch=100, velocity=100),
    ]

    def check_res(clip, res):
        # type: (AutomationMidiClip, Dict[str, List[Note]]) -> None
        assert len(res["set_notes"]) == 1
        assert len(clip._prev_notes) == 2
        assert res["set_notes"][0].pitch == 70
        assert clip._prev_notes[0].pitch == 70
        assert res["set_notes"][0].velocity == 70
        assert clip._prev_notes[0].velocity == 70

    notes = Note.copy_notes(prev_notes)
    notes[0].pitch = 70
    (clip, res) = create_automation_midi_clip_with_notes(notes, prev_notes)
    clip._map_notes(notes)
    check_res(clip, res)


def test_modify_note_velocity():
    # type: () -> None
    prev_notes = [
        Note(start=0, duration=2, pitch=80, velocity=80),
        Note(start=2, duration=2, pitch=100, velocity=100),
    ]

    def check_res(clip, res):
        # type: (AutomationMidiClip, Dict[str, List[Note]]) -> None
        assert len(res["set_notes"]) == 1
        assert len(clip._prev_notes) == 2
        assert res["set_notes"][0].pitch == 70
        assert clip._prev_notes[0].pitch == 70
        assert res["set_notes"][0].velocity == 70
        assert clip._prev_notes[0].velocity == 70

    notes = Note.copy_notes(prev_notes)
    notes[0].velocity = 70
    (clip, res) = create_automation_midi_clip_with_notes(notes, prev_notes)
    clip._map_notes(notes)
    check_res(clip, res)


def test_insert_min_note():
    # type: () -> None
    notes = [
        Note(start=2, duration=2, pitch=100, velocity=100),
    ]

    (clip, res) = create_automation_midi_clip_with_notes(notes, loop_start=0)
    clip._map_notes(notes)
    assert_note(clip._prev_notes[0], {"start": 0, "duration": 2, "pitch": 0, "velocity": 0})
