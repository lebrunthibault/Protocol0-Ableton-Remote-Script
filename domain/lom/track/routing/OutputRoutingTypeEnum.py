from protocol0.shared.AbstractEnum import AbstractEnum


class OutputRoutingTypeEnum(AbstractEnum):
    MASTER = "Master"
    SENDS_ONLY = "Sends Only"

    @property
    def label(self):
        # type: () -> str
        return self.value
