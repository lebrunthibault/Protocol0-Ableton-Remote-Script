from protocol0.enums.AbstractEnum import AbstractEnum


class InputRoutingTypeEnum(AbstractEnum):
    # AUDIO
    NO_INPUT = "No Input"
    ALL_INS = "All Ins"

    @property
    def label(self):
        # type: () -> str
        return self.value
