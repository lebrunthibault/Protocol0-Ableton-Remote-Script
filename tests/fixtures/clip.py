from _Framework.SubjectSlot import Subject


class AbletonClip(Subject):
    __subject_events__ = ("notes", "name")

    def __init__(self, length):
        self.length = length
        self.is_midi_clip = True
        self.color_index = 0

    def get_notes(self, *a, **k):
        return []
