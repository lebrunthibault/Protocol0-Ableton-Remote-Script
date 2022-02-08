from protocol0.shared.AbstractEnum import AbstractEnum


class RecordingBarLengthEnum(AbstractEnum):
    _order_ = "ONE, TWO, FOUR, EIGHT, SIXTEEN, THIRTY_TWO, SIXTY_FOUR, UNLIMITED"

    ONE = 1
    TWO = 2
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16
    THIRTY_TWO = 32
    SIXTY_FOUR = 64
    UNLIMITED = 0

    @property
    def bar_length_value(self):
        # type: () -> int
        return self.value

    @classmethod
    def int_to_str(cls, int_value):
        # type: (int) -> str
        return "%s bar%s" % (int_value, "s" if abs(int_value) != 1 else "")

    def __str__(self):
        # type: () -> str
        if self == RecordingBarLengthEnum.UNLIMITED:
            return "unlimited bars"
        else:
            return self.int_to_str(self.value)
