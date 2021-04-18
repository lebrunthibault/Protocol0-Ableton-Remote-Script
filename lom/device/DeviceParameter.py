import Live
from typing import TYPE_CHECKING, Any, Optional

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.utils import scale_from_value

if TYPE_CHECKING:
    from a_protocol_0.lom.device.Device import Device


class DeviceParameter(AbstractObject):
    def __init__(self, device, device_parameter, *a, **k):
        # type: (Device, Live.DeviceParameter.DeviceParameter, Any, Any) -> None
        super(DeviceParameter, self).__init__(*a, **k)
        self.device = device
        self.track = self.device.track
        self._device_parameter = device_parameter

    def __repr__(self):
        return "%s: %s" % (self.name, self.value)

    @property
    def name(self):
        # type: () -> str
        return self._device_parameter.name

    @property
    def full_name(self):
        # type: () -> str
        return "%s.%s" % (self._device_parameter.name, self.device.name)

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

    def get_value_from_midi_value(self, midi_value):
        # type: (int) -> float
        return scale_from_value(midi_value, 0, 127, self.min, self.max)

    def get_midi_value_from_value(self, value=None):
        # type: (Optional[float]) -> int
        value = value if value is not None else self.value
        return int(scale_from_value(value, self.min, self.max, 0, 127))

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
