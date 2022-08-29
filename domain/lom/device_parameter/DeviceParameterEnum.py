from typing import List, Optional, Any

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.AbstractEnum import AbstractEnum


class DeviceParameterEnum(AbstractEnum):
    AUTO_FILTER_HIGH_PASS_FREQUENCY = "AUTO FILTER HIGH PASS FREQUENCY"
    AUTO_FILTER_LOW_PASS_FREQUENCY = "AUTO FILTER LOW PASS FREQUENCY"
    CHAIN_SELECTOR = "CHAIN SELECTOR"
    COMPRESSOR_OUTPUT_GAIN = "COMPRESSOR OUTPUT GAIN"
    COMPRESSOR_THRESHOLD = "COMPRESSOR THRESHOLD"
    DEVICE_ON = "DEVICE ON"
    EFFECTRIX_GLOBALWET = "EFFECTRIX GLOBALWET"
    EQ_EIGHT_FREQUENCY_1_A = "EQ EIGHT FREQUENCY 1 A"
    EQ_EIGHT_FREQUENCY_8_A = "EQ EIGHT FREQUENCY 8 A"
    EQ_EIGHT_GAIN_4_A = "EQ EIGHT GAIN 4 A"
    LFO_TOOL_LFO_DEPTH = "LFO TOOL LFO DEPTH"
    UTILITY_GAIN = "UTILITY GAIN"
    UTILITY_SILENT_GAIN = "UTILITY SILENT GAIN"
    UTILITY_MID_SIDE = "UTILITY MID SIDE"

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
                DeviceParameterEnum.UTILITY_GAIN: "Gain",
                DeviceParameterEnum.UTILITY_SILENT_GAIN: "Gain",
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
            }
        )

    @classmethod
    def automatable_parameters(cls):
        # type: () -> List[DeviceParameterEnum]
        return [
            cls.UTILITY_GAIN,
            cls.AUTO_FILTER_LOW_PASS_FREQUENCY,
            cls.AUTO_FILTER_HIGH_PASS_FREQUENCY,
        ]

    @classmethod
    def from_name(cls, device_name, name):
        # type: (str, str) -> Optional[DeviceParameterEnum]
        enum_name = "%s %s" % (device_name.upper(), name.upper())
        try:
            return DeviceParameterEnum.from_value(enum_name)
        except Protocol0Error:
            return None

    @property
    def default_value(self):
        # type: () -> Any
        return self.get_value_from_mapping(
            {
                DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: 20,
                DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: 135,
                DeviceParameterEnum.EFFECTRIX_GLOBALWET: 0,
                DeviceParameterEnum.UTILITY_SILENT_GAIN: -1,
            }
        )
