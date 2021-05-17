from typing import List, Optional, Tuple, Dict, Any

from _Framework.SubjectSlot import Subject
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.tests.fixtures import make_song
from a_protocol_0.tests.fixtures.clip_slot import make_clip_slot


class AbletonClip(Subject):
    __subject_events__ = (
        "notes",
        "name",
        "color",
        "is_recording",
        "playing_status",
        "loop_start",
        "loop_end",
        "warping",
        "looping",
        "start_marker",
        "end_marker",
    )

    def __init__(self, length, loop_start):
        # type: (float, float) -> None
        self.length = length
        self.color_index = 0
        self.loop_start = loop_start
        self.loop_end = self.loop_start + length
        self.name = "pytest"
        self.view = None
        self.is_recording = False

    def get_notes(self, *a, **k):
        # type: (Any, Any) -> List[Any]
        return []

    def remove_notes(self, *a, **k):
        # type: (Any, Any) -> None
        pass


def create_automation_midi_clip_with_notes(notes, prev_notes=[], clip_length=None, loop_start=None):
    # type: (List[Note], List[Note], Optional[float], Optional[float]) -> Tuple[AutomationMidiClip, Dict[str, List[Note]]]
    song = make_song(count_simple_tracks=1)
    track = next(song.simple_tracks)
    loop_start = loop_start if loop_start is not None else notes[0].start
    length = clip_length or notes[-1].end - loop_start
    cs = make_clip_slot(track=track, clip_length=length, clip_loop_start=loop_start)
    clip = AutomationMidiClip(clip_slot=cs)
    clip._prev_notes = Note.copy_notes(prev_notes)
    for note in notes:
        note.clip = clip
    test_res = {"set_notes": []}  # type: Dict[str, List[Note]]
    clip.map_notes.__func__.wait_time = 0

    def replace_all_notes(notes):
        # type: (List[Note]) -> None
        clip._prev_notes = notes

    def set_notes(notes):
        # type: (List[Note]) -> None
        test_res["set_notes"] = notes

    clip.replace_all_notes = replace_all_notes  # type: ignore[assignment]
    clip.set_notes = set_notes  # type: ignore[assignment]

    return (clip, test_res)
