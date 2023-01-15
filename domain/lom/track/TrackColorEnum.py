from protocol0.domain.shared.ui.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class TrackColorEnum(ColorEnumInterface, AbstractEnum):
    RETURN = 10
    DISABLED = 13
    DRUMS = 61
    VOCALS = 61

    @property
    def int_value(self):
        # type: () -> int
        return self.value
