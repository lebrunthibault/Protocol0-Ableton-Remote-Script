from protocol0.domain.enums.AbstractEnum import AbstractEnum


class Push2MainModeEnum(AbstractEnum):
    DEVICE = "device"
    MIX = "mix"

    @property
    def label(self):
        # type: () -> str
        return self.value
