from protocol0.enums.AbstractEnum import AbstractEnum


class DeviceParameterEnum(AbstractEnum):
    DEVICE_ON = "DEVICE_ON"
    CHAIN_SELECTOR = "CHAIN_SELECTOR"
    COMPRESSOR_OUTPUT_GAIN = "COMPRESSOR_OUTPUT_GAIN"
    COMPRESSOR_THRESHOLD = "COMPRESSOR_THRESHOLD"
    DUMMY_RACK_GAIN = "DUMMY_RACK_GAIN"
    EQ_EIGHT_FREQUENCY_1_A = "EQ_EIGHT_FREQUENCY_1_A"
    EQ_EIGHT_FREQUENCY_8_A = "EQ_EIGHT_FREQUENCY_8_A"
    LFO_TOOL_LFO_DEPTH = "LFO_TOOL_LFO_DEPTH"
    UTILITY_GAIN = "UTILITY_GAIN"

    @property
    def label(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceParameterEnum.DEVICE_ON: "Device On",
            DeviceParameterEnum.CHAIN_SELECTOR: "Chain Selector",
            DeviceParameterEnum.COMPRESSOR_OUTPUT_GAIN: "Output Gain",
            DeviceParameterEnum.COMPRESSOR_THRESHOLD: "Threshold",
            DeviceParameterEnum.DUMMY_RACK_GAIN: "Gain",
            DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A: "1 Frequency A",
            DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A: "8 Frequency A",
            DeviceParameterEnum.LFO_TOOL_LFO_DEPTH: "LFO Depth",
            DeviceParameterEnum.UTILITY_GAIN: "Gain",
        })
