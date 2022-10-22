from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # for python 3 import
    from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.shared.utils.utils import compare_values


class DeviceParameterValue(object):
    def __init__(self, device_parameter_enum, value):
        # type: (DeviceParameterEnum, Any) -> None
        self._device_parameter_enum = device_parameter_enum
        self._value = value

    def matches(self, device):
        # type: (Device) -> bool
        device_parameter = device.get_parameter_by_name(
            device_parameter_name=self._device_parameter_enum
        )
        return (
            compare_values(device_parameter.value, self._value)
            and device_parameter.is_enabled
            and not device_parameter.is_automated
        )
