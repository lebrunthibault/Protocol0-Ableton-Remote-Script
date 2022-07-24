from typing import List

from protocol0.shared.AbstractEnum import AbstractEnum


class DeviceParameterEnum(AbstractEnum):
    AUTO_FILTER_HIGH_PASS_FREQUENCY = "AUTO_FILTER_HIGH_PASS_FREQUENCY"
    AUTO_FILTER_LOW_PASS_FREQUENCY = "AUTO_FILTER_LOW_PASS_FREQUENCY"
    CHAIN_SELECTOR = "CHAIN_SELECTOR"
    COMPRESSOR_OUTPUT_GAIN = "COMPRESSOR_OUTPUT_GAIN"
    COMPRESSOR_THRESHOLD = "COMPRESSOR_THRESHOLD"
    DEVICE_ON = "DEVICE_ON"
    EQ_EIGHT_FREQUENCY_1_A = "EQ_EIGHT_FREQUENCY_1_A"
    EQ_EIGHT_FREQUENCY_8_A = "EQ_EIGHT_FREQUENCY_8_A"
    EQ_EIGHT_GAIN_4_A = "EQ_EIGHT_GAIN_4_A"
    LFO_TOOL_LFO_DEPTH = "LFO_TOOL_LFO_DEPTH"
    LFO_TOOL_DEVICE_ON = "LFO_TOOL_DEVICE_ON"
    UTILITY_GAIN = "UTILITY_GAIN"
    UTILITY_MID_SIDE = "UTILITY_MID_SIDE"

    @property
    def parameter_name(self):
        # type: () -> str
        return self.get_value_from_mapping(
            {
                DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: "Frequency",
                DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: "Frequency",
                DeviceParameterEnum.CHAIN_SELECTOR: "Chain Selector",
                DeviceParameterEnum.COMPRESSOR_OUTPUT_GAIN: "Output Gain",
                DeviceParameterEnum.COMPRESSOR_THRESHOLD: "Threshold",
                DeviceParameterEnum.DEVICE_ON: "Device On",
                DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A: "1 Frequency A",
                DeviceParameterEnum.EQ_EIGHT_GAIN_4_A: "4 Gain A",
                DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A: "8 Frequency A",
                DeviceParameterEnum.LFO_TOOL_DEVICE_ON: "Device On",
                DeviceParameterEnum.UTILITY_GAIN: "Gain",
                DeviceParameterEnum.UTILITY_MID_SIDE: "Mid/Side Balance",
            }
        )

    @property
    def label(self):
        # type: () -> str
        return self.get_value_from_mapping(
            {
                DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: "Low Pass Frequency",
                DeviceParameterEnum.UTILITY_GAIN: "Gain",
                DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: "High Pass Frequency",
                DeviceParameterEnum.LFO_TOOL_DEVICE_ON: "Lfo Tool",
            }
        )

    @classmethod
    def automatable_parameters(cls):
        # type: () -> List[DeviceParameterEnum]
        return [
            cls.UTILITY_GAIN,
            cls.AUTO_FILTER_LOW_PASS_FREQUENCY,
            cls.AUTO_FILTER_HIGH_PASS_FREQUENCY,
            cls.LFO_TOOL_DEVICE_ON
        ]
