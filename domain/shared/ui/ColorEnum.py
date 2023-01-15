from protocol0.domain.shared.ui.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class ColorEnum(ColorEnumInterface, AbstractEnum):
    WARNING = 12
    FOCUSED = 26

    @property
    def int_value(self):
        # type: () -> int
        return self.value
