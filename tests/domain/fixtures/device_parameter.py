from _Framework.SubjectSlot import Subject


class AbletonDeviceParameter(Subject):
    def __init__(self, name):
        # type: (str) -> None
        self._live_ptr = id(self)
        self.name = name
        self.is_enabled = True
        self.default_value = 0
        self.min = 0
        self.max = 1
