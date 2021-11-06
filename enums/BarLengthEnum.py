from protocol0.enums.AbstractEnum import AbstractEnum


class BarLengthEnum(AbstractEnum):
    _order_ = "ONE, TWO, FOUR, EIGHT, SIXTEEN, THIRTY_TWO, SIXTY_FOUR, UNLIMITED"

    ONE = 1
    TWO = 2
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16
    THIRTY_TWO = 32
    SIXTY_FOUR = 64
    UNLIMITED = "UNLIMITED"

    def __str__(self):
        # type: () -> str
        if self == BarLengthEnum.UNLIMITED:
            return "unlimited bars"
        else:
            return "%s bar%s" % (self.value, "s" if abs(self.value) != 1 else "")
