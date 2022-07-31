from protocol0.domain.shared.ui.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class TrackColorEnum(ColorEnumInterface, AbstractEnum):
    RETURN = 10
    DISABLED = 13

    @property
    def color_int_value(self):
        # type: () -> int
        return self.value
