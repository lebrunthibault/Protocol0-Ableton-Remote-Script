from protocol0.enums.AbstractEnum import AbstractEnum


class ColorEnum(AbstractEnum):
    SIMPLER = 2
    DRUM_RACK = 3
    DEFAULT = 10
    DISABLED = 13
    ERROR = 14
    SERUM = 18
    PROPHET = 23
    ADDICTIVE_KEYS = 26
    MINITAUR = 69

    @property
    def index(self):
        # type: () -> int
        return self.value
