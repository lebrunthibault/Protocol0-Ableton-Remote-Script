from typing import TYPE_CHECKING, Any

import Live
from protocol0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from protocol0.lom.device.Device import Device


class DeviceParameter(AbstractObject):
    def __init__(self, device, device_parameter, *a, **k):
        # type: (Device, Live.DeviceParameter.DeviceParameter, Any, Any) -> None
        super(DeviceParameter, self).__init__(*a, **k)
        self.device = device
        self.track = self.device.track
        self._device_parameter = device_parameter  # type: Live.DeviceParameter.DeviceParameter

    def __repr__(self):
        # type: () -> str
        return "%s: %s" % (self.name, self.value)

    @property
    def name(self):
        # type: () -> str
        return self._device_parameter.name

    @property
    def original_name(self):
        # type: () -> str
        return self._device_parameter.original_name

    @property
    def value(self):
        # type: () -> float
        return self._device_parameter.value

    @value.setter
    def value(self, value):
        # type: (float) -> None
        self._device_parameter.value = value

    @property
    def default_value(self):
        # type: () -> float
        return self._device_parameter.default_value

    @property
    def min(self):
        # type: () -> float
        return self._device_parameter.min

    @property
    def max(self):
        # type: () -> float
        return self._device_parameter.max

    @property
    def is_quantized(self):
        # type: () -> bool
        return self._device_parameter.is_quantized

    @property
    def is_enabled(self):
        # type: () -> bool
        return self._device_parameter.is_enabled
