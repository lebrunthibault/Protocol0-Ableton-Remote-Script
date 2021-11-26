from typing import Any

from protocol0.lom.device.Device import Device


class DeviceParameterValue(object):
    def __init__(self, device_parameter_enum, value):
        self._device_parameter_enum = device_parameter_enum
        self._value = value

    def matches(self, device):
        # type: (Device) -> bool
        device_parameter = device.get_parameter_by_name(device_parameter_name=self._device_parameter_enum)
        return self._compare_values(device_parameter.value, self._value)

    @classmethod
    def _compare_values(cls, value, expected_value):
        # type: (Any, Any) -> bool
        if isinstance(value, float):
            value = round(value, 3)
            expected_value = round(expected_value, 3)

        return value == expected_value
