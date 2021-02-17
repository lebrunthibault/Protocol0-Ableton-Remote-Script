from typing import TYPE_CHECKING

import Live

from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.device.Device import Device


class DeviceParameter(AbstractObject):
    def __init__(self, device, device_parameter, *a, **k):
        # type: (Device, Live.DeviceParameter.DeviceParameter) -> None
        super(DeviceParameter, self).__init__(*a, **k)
        self.device = device
        self.track = self.device.track
        self._device_parameter = device_parameter
        self.canonical_parent = self._device_parameter.canonical_parent

    def __repr__(self):
        return "%s: %s" % (self.name, self.value)

    @property
    def name(self):
        return self._device_parameter.name

    @property
    def original_name(self):
        return self._device_parameter.original_name

    @property
    def value(self):
        return self._device_parameter.value

    @value.setter
    def value(self, value):
        self._device_parameter.value = value

    @property
    def min(self):
        return self._device_parameter.min

    @property
    def max(self):
        return self._device_parameter.max

    @property
    def is_quantized(self):
        return self._device_parameter.is_quantized

    @property
    def is_enabled(self):
        return self._device_parameter.is_enabled
