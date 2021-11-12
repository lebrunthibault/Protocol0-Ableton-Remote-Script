from protocol0.enums.AbstractEnum import AbstractEnum


class DeviceParameterNameEnum(AbstractEnum):
    LFO_TOOL_LFO_DEPTH = "LFO Depth"

    @property
    def label(self):
        # type: () -> str
        return self.value
