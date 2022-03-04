from protocol0.domain.lom.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class ColorEnum(ColorEnumInterface, AbstractEnum):
    WARNING = 12

    @property
    def color_int_value(self):
        # type: () -> int
        return self.value
