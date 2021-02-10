from _Framework.SubjectSlot import Subject


class AbletonClip(Subject):
    __subject_events__ = ("notes", "name")

    def __init__(self, length, name):
        self.length = length
        self.is_midi_clip = True
        self.color_index = 0
        self.loop_start = 0
        self.name = name

    def get_notes(self, *a, **k):
        return []

    def remove_notes(self, *a, **k):
        pass