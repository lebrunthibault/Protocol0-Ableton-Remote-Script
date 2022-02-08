from _Framework.SubjectSlot import Subject


class AbletonScene(Subject):
    __subject_events__ = ("name", "is_triggered")

    def __init__(self):
        self._live_ptr = id(self)
        self.name = "test scene"
