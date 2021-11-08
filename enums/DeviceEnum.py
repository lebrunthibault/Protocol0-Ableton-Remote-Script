from typing import List

from protocol0.enums.AbstractEnum import AbstractEnum
from protocol0.lom.device.Device import Device


class DeviceEnum(AbstractEnum):
    EXTERNAL_AUDIO_EFFECT = "Ext. Audio Effect"
    EXTERNAL_INSTRUMENT = "Ext. Instrument"
    LFO_TOOL = "LFOTool_x64"
    MIX_RACK = "Mix Rack"

    @property
    def _is_rack(self):
        # type: () -> bool
        return self in [DeviceEnum.MIX_RACK]

    @property
    def is_updatable(self):
        # type: () -> bool
        return self in [DeviceEnum.MIX_RACK]

    @classmethod
    def updatable_device_enums(cls):
        # type: () -> List[DeviceEnum]
        return [enum for enum in list(DeviceEnum) if enum.is_updatable]

    @property
    def device_name(self):
        # type: () -> str
        return self.value

    @property
    def browser_name(self):
        # type: () -> str
        if self._is_rack:
            return "'%s.adg'" % self.device_name
        else:
            return self.device_name

    def matches_device(self, device):
        # type: (Device) -> bool
        return device.name == self.device_name
