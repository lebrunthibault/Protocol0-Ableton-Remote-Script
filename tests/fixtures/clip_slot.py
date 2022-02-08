from _Framework.SubjectSlot import Subject


class AbletonClipSlot(Subject):
    __subject_events__ = ("has_clip", "is_triggered")

    def __init__(self):
        self.clip = None
        self.has_clip = None
