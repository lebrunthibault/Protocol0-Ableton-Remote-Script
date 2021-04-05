from _Framework.SubjectSlot import Subject


class AbletonClip(Subject):
    __subject_events__ = ("notes", "name", "color", "is_recording", "loop_start", "loop_end", "warping", "start_marker", "end_marker")

    def __init__(self, length, name, loop_start):
        self.length = length
        self.is_midi_clip = True
        self.color_index = 0
        self.loop_start = loop_start
        self.loop_end = self.loop_start + length
        self.name = name
        self.view = None
        self.is_recording = False

    def get_notes(self, *a, **k):
        return []

    def remove_notes(self, *a, **k):
        pass