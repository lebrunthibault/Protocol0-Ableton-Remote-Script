from protocol0.domain.lom.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class TrackColorEnum(ColorEnumInterface, AbstractEnum):
    DEFAULT = 10
    DISABLED = 13
    ERROR = 14

    @property
    def color_int_value(self):
        # type: () -> int
        return self.value
