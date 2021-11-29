from typing import List

from protocol0.enums.AbstractEnum import AbstractEnum
from protocol0.enums.DeviceParameterEnum import DeviceParameterEnum
from protocol0.lom.device.Device import Device
from protocol0.lom.device.DeviceParameterValue import DeviceParameterValue


class DeviceEnum(AbstractEnum):
    ARPEGGIATOR_RACK = "ARPEGGIATOR_RACK"
    COMPRESSOR = "COMPRESSOR"
    DUMMY_RACK = "DUMMY_RACK"
    EQ_EIGHT = "EQ_EIGHT"
    EXTERNAL_AUDIO_EFFECT = "EXTERNAL_AUDIO_EFFECT"
    EXTERNAL_INSTRUMENT = "EXTERNAL_INSTRUMENT"
    LFO_TOOL = "LFO_TOOL"
    MINITAUR_EDITOR = "MINITAUR_EDITOR"
    MIX_RACK = "MIX_RACK"
    REV2_EDITOR = "REV2_EDITOR"
    USAMO = "USAMO"
    UTILITY = "UTILITY"

    @property
    def is_rack(self):
        # type: () -> bool
        return self in [DeviceEnum.ARPEGGIATOR_RACK, DeviceEnum.MIX_RACK, DeviceEnum.DUMMY_RACK]

    @property
    def is_device(self):
        # type: () -> bool
        return self in [DeviceEnum.EXTERNAL_AUDIO_EFFECT, DeviceEnum.EXTERNAL_INSTRUMENT]

    @classmethod
    def updatable_devices(cls):
        # type: () -> List[DeviceEnum]
        return [cls.MIX_RACK, cls.LFO_TOOL]

    @classmethod
    def plugin_white_list(cls):
        # type: () -> List[DeviceEnum]
        return [
            cls.REV2_EDITOR,
            cls.USAMO
        ]

    @property
    def device_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.ARPEGGIATOR_RACK: "Arpeggiator rack",
            DeviceEnum.COMPRESSOR: "Compressor",
            DeviceEnum.DUMMY_RACK: "Dummy Rack",
            DeviceEnum.EQ_EIGHT: "EQ Eight",
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "Ext. Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "Ext. Instrument",
            DeviceEnum.LFO_TOOL: "LFOTool_x64",
            DeviceEnum.MINITAUR_EDITOR: "Minitaur Editor(x64)",
            DeviceEnum.MIX_RACK: "Mix Rack",
            DeviceEnum.REV2_EDITOR: "REV2Editor",
            DeviceEnum.USAMO: "usamo_x64",
            DeviceEnum.UTILITY: "Utility",
        })

    @property
    def browser_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "External Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "External Instrument",
            DeviceEnum.DUMMY_RACK: "Dummy Rack.adg",
            DeviceEnum.LFO_TOOL: "LFOTool.adg",
            DeviceEnum.MIX_RACK: "Mix Rack.adg",
        })

    @classmethod
    def deprecated_devices(cls):
        # type: () -> List[DeviceEnum]
        return [cls.MINITAUR_EDITOR]

    @property
    def main_parameters_default(self):
        # type: () -> List[DeviceParameterValue]
        return self.get_value_from_mapping({
            DeviceEnum.ARPEGGIATOR_RACK: [DeviceParameterValue(DeviceParameterEnum.CHAIN_SELECTOR, 0)],
            DeviceEnum.COMPRESSOR: [
                DeviceParameterValue(DeviceParameterEnum.COMPRESSOR_OUTPUT_GAIN, 0),
                DeviceParameterValue(DeviceParameterEnum.COMPRESSOR_THRESHOLD, 0.850000023842),  # 0db
            ],
            DeviceEnum.EQ_EIGHT: [
                DeviceParameterValue(DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A, 0.285494267941),
                DeviceParameterValue(DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A, 1),
            ],  # 90 Hz
            DeviceEnum.LFO_TOOL: [DeviceParameterValue(DeviceParameterEnum.LFO_TOOL_LFO_DEPTH, 0)],
            DeviceEnum.UTILITY: [DeviceParameterValue(DeviceParameterEnum.UTILITY_GAIN, 0)],
        })

    def matches_device(self, device):
        # type: (Device) -> bool
        return device.name == self.device_name
