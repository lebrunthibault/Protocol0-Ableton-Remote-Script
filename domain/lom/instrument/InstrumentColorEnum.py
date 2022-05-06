from protocol0.domain.shared.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class InstrumentColorEnum(ColorEnumInterface, AbstractEnum):
    UNKNOWN = 13
    SIMPLER = 2
    SERUM = 18
    PROPHET = 23
    ADDICTIVE_KEYS = 26
    MINITAUR = 69

    @property
    def color_int_value(self):
        # type: () -> int
        return self.value
