from protocol0.domain.shared.ui.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class InstrumentColorEnum(ColorEnumInterface, AbstractEnum):
    UNKNOWN = 13
    SIMPLER = 2
    SERUM = 18
    PROPHET = 23
    OPUS = 23
    PLAY = 23
    KONTAKT = 26
    MINITAUR = 69

    @property
    def color_int_value(self):
        # type: () -> int
        return self.value
