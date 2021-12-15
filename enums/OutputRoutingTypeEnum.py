from protocol0.enums.AbstractEnum import AbstractEnum


class OutputRoutingTypeEnum(AbstractEnum):
    MASTER = "Master"

    @property
    def label(self):
        # type: () -> str
        return self.value
