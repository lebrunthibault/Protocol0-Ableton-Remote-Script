from typing import List, Tuple

from protocol0.enums.AbstractEnum import AbstractEnum
from protocol0.enums.DeviceParameterNameEnum import DeviceParameterNameEnum
from protocol0.lom.device.Device import Device


class DeviceEnum(AbstractEnum):
    EXTERNAL_AUDIO_EFFECT = "EXTERNAL_AUDIO_EFFECT"
    EXTERNAL_INSTRUMENT = "EXTERNAL_INSTRUMENT"
    LFO_TOOL = "LFO_TOOL"
    MIX_RACK = "MIX_RACK"
    USAMO = "USAMO"

    @property
    def is_rack(self):
        # type: () -> bool
        return self in [DeviceEnum.MIX_RACK]

    @property
    def is_device(self):
        # type: () -> bool
        return self in [DeviceEnum.EXTERNAL_AUDIO_EFFECT, DeviceEnum.EXTERNAL_INSTRUMENT]

    @property
    def is_updatable(self):
        # type: () -> bool
        return self in [DeviceEnum.MIX_RACK, DeviceEnum.LFO_TOOL]

    @classmethod
    def updatable_device_enums(cls):
        # type: () -> List[DeviceEnum]
        return [enum for enum in list(DeviceEnum) if enum.is_updatable]

    @property
    def device_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "Ext. Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "Ext. Instrument",
            DeviceEnum.LFO_TOOL: "LFOTool_x64",
            DeviceEnum.MIX_RACK: "Mix Rack",
            DeviceEnum.USAMO: "usamo_x64",
        })

    @property
    def browser_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "External Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "External Instrument",
            DeviceEnum.LFO_TOOL: "LFOTool.adg",
            DeviceEnum.MIX_RACK: "Mix Rack.adg",
        })

    @property
    def main_parameter_default(self):
        # type: () -> Tuple[DeviceParameterNameEnum, int]
        return self.get_value_from_mapping({
            DeviceEnum.LFO_TOOL: (DeviceParameterNameEnum.LFO_TOOL_LFO_DEPTH, 0),
        })

    def matches_device(self, device):
        # type: (Device) -> bool
        return device.name == self.device_name
