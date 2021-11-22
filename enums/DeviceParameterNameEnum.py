from protocol0.enums.AbstractEnum import AbstractEnum


class DeviceParameterNameEnum(AbstractEnum):
    DUMMY_RACK_GAIN = "DUMMY_RACK_GAIN"
    LFO_TOOL_LFO_DEPTH = "LFO_TOOL_LFO_DEPTH"

    @property
    def label(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceParameterNameEnum.DUMMY_RACK_GAIN: "Gain",
            DeviceParameterNameEnum.LFO_TOOL_LFO_DEPTH: "LFO Depth",
        })
