from typing import Any

from protocol0.components.UtilsManager import UtilsManager
from protocol0.enums.DeviceParameterEnum import DeviceParameterEnum
from protocol0.lom.device.Device import Device


class DeviceParameterValue(object):
    def __init__(self, device_parameter_enum, value):
        # type: (DeviceParameterEnum, Any) -> None
        self._device_parameter_enum = device_parameter_enum
        self._value = value

    def matches(self, device):
        # type: (Device) -> bool
        device_parameter = device.get_parameter_by_name(device_parameter_name=self._device_parameter_enum)
        return UtilsManager.compare_values(device_parameter.value,
                                           self._value) and device_parameter.is_enabled and not device_parameter.is_automated
