from typing import List, TYPE_CHECKING

from protocol0.enums.AbstractEnum import AbstractEnum

if TYPE_CHECKING:
    from protocol0.enums.DeviceEnum import DeviceEnum  # noqa


class DeviceParameterEnum(AbstractEnum):
    AUTO_FILTER_HIGH_PASS_FREQUENCY = "AUTO_FILTER_HIGH_PASS_FREQUENCY"
    AUTO_FILTER_LOW_PASS_FREQUENCY = "AUTO_FILTER_LOW_PASS_FREQUENCY"
    CHAIN_SELECTOR = "CHAIN_SELECTOR"
    COMPRESSOR_OUTPUT_GAIN = "COMPRESSOR_OUTPUT_GAIN"
    COMPRESSOR_THRESHOLD = "COMPRESSOR_THRESHOLD"
    DEVICE_ON = "DEVICE_ON"
    DUMMY_RACK_GAIN = "DUMMY_RACK_GAIN"
    EQ_EIGHT_FREQUENCY_1_A = "EQ_EIGHT_FREQUENCY_1_A"
    EQ_EIGHT_FREQUENCY_8_A = "EQ_EIGHT_FREQUENCY_8_A"
    LFO_TOOL_LFO_DEPTH = "LFO_TOOL_LFO_DEPTH"
    UTILITY_GAIN = "UTILITY_GAIN"
    UTILITY_MID_SIDE = "UTILITY_MID_SIDE"

    @property
    def device_enum(self):
        # type: () -> DeviceEnum
        from protocol0.enums.DeviceEnum import DeviceEnum  # noqa

        return self.get_value_from_mapping({
            DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: DeviceEnum.AUTO_FILTER_HIGH_PASS,
            DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: DeviceEnum.AUTO_FILTER_LOW_PASS,
            DeviceParameterEnum.UTILITY_GAIN: DeviceEnum.UTILITY,
        })

    @property
    def label(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: "Frequency",
            DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: "Frequency",
            DeviceParameterEnum.CHAIN_SELECTOR: "Chain Selector",
            DeviceParameterEnum.COMPRESSOR_OUTPUT_GAIN: "Output Gain",
            DeviceParameterEnum.COMPRESSOR_THRESHOLD: "Threshold",
            DeviceParameterEnum.DEVICE_ON: "Device On",
            DeviceParameterEnum.DUMMY_RACK_GAIN: "Gain",
            DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A: "1 Frequency A",
            DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A: "8 Frequency A",
            DeviceParameterEnum.LFO_TOOL_LFO_DEPTH: "LFO Depth",
            DeviceParameterEnum.UTILITY_GAIN: "Gain",
            DeviceParameterEnum.UTILITY_MID_SIDE: "Mid/Side Balance",
        })

    @classmethod
    def automatable_parameters(cls):
        # type: () -> List[DeviceParameterEnum]
        return [
            cls.AUTO_FILTER_HIGH_PASS_FREQUENCY,
            cls.AUTO_FILTER_LOW_PASS_FREQUENCY,
            cls.UTILITY_GAIN,
        ]
