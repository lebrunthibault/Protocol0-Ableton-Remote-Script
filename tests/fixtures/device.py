from _Framework.SubjectSlot import Subject


class AbletonDevice(Subject):
    def __init__(self, class_name):
        # type: (str) -> None
        self.class_name = class_name
        self.name = class_name


def make_device_simpler():
    # type: () -> AbletonDevice
    return AbletonDevice("OriginalSimpler")
