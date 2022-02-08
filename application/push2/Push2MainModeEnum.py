from protocol0.shared.AbstractEnum import AbstractEnum


class Push2MainModeEnum(AbstractEnum):
    DEVICE = "device"
    MIX = "mix"

    @property
    def label(self):
        # type: () -> str
        return self.value
