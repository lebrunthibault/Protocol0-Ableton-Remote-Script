from _Framework.SubjectSlot import Subject

from protocol0.tests.domain.fixtures.clip import AbletonClip


class AbletonClipSlot(Subject):
    __subject_events__ = ("has_clip", "is_triggered")

    def __init__(self):
        self.clip = None
        self.has_clip = None
        self.has_stop_button = True
        self.playing_position = 0

    def add_clip(self):
        self.clip = AbletonClip()
        self.has_clip = True
