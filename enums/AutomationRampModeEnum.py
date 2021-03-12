from a_protocol_0.enums.AbstractEnum import AbstractEnum


class AutomationRampModeEnum(AbstractEnum):
    NO_RAMP = ""
    END_RAMP = "*"
    LINEAR_RAMP = "/"

    @classmethod
    def default(cls):
        return AutomationRampModeEnum.NO_RAMP
