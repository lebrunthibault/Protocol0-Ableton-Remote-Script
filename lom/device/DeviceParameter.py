from typing import TYPE_CHECKING

import Live

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.utils import scale_from_value

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

    def __repr__(self):
        return "%s: %s" % (self.name, self.value)

    @property
    def name(self):
        return self._device_parameter.name

    @property
    def full_name(self):
        return "%s.%s" % (self._device_parameter.name, self.device.name)

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
    def default_value(self):
        return self._device_parameter.default_value

    @property
    def default_midi_value(self):
        pass

    def get_value_from_midi_value(self, midi_value):
        # type: (int) -> float
        return scale_from_value(midi_value, 0, 127, self.min, self.max)

    def get_midi_value_from_value(self):
        # type: () -> float
        return scale_from_value(self.value, self.min, self.max, 0, 127)

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
