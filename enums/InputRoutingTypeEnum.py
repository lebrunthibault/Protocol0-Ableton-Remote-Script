from protocol0.enums.AbstractEnum import AbstractEnum


class InputRoutingTypeEnum(AbstractEnum):
    # AUDIO
    EXT_IN = "Ext. In"
    NO_INPUT = "No Input"

    @property
    def label(self):
        # type: () -> str
        return self.value
