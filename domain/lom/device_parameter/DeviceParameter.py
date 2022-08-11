import Live
from typing import Any


class DeviceParameter(object):
    def __init__(self, device_parameter, is_mixer_parameter=False):
        # type: (Live.DeviceParameter.DeviceParameter, bool) -> None
        self._device_parameter = device_parameter  # type: Live.DeviceParameter.DeviceParameter
        self._is_mixer_parameter = is_mixer_parameter

    def __repr__(self, **k):
        # type: (Any) -> str
        return "%s: %s" % (self.name, self.value)

    @property
    def name(self):
        # type: () -> str
        if self._device_parameter:
            return self._device_parameter.name
        else:
            return ""

    @property
    def original_name(self):
        # type: () -> str
        if self._device_parameter:
            return self._device_parameter.original_name
        else:
            return ""

    @property
    def value(self):
        # type: () -> float
        if self._device_parameter:
            return self._device_parameter.value
        else:
            return 0

    @value.setter
    def value(self, value):
        # type: (float) -> None
        if self.is_enabled and self._device_parameter:
            self._device_parameter.value = value

    @property
    def default_value(self):
        # type: () -> float
        if self._device_parameter:
            return self._device_parameter.default_value
        else:
            return 0

    @property
    def automation_state(self):
        # type: () -> float
        if self._device_parameter:
            return self._device_parameter.automation_state
        else:
            return 0

    @property
    def is_automated(self):
        # type: () -> bool
        return self.automation_state != Live.DeviceParameter.AutomationState.none

    @property
    def min(self):
        # type: () -> float
        if self._device_parameter:
            return self._device_parameter.min
        else:
            return 0

    @property
    def max(self):
        # type: () -> float
        if self._device_parameter:
            return self._device_parameter.max
        else:
            return 0

    @property
    def is_quantized(self):
        # type: () -> bool
        if self._device_parameter:
            return self._device_parameter.is_quantized
        else:
            return False

    @property
    def is_enabled(self):
        # type: () -> bool
        if self._device_parameter:
            return self._device_parameter.is_enabled
        else:
            return False

    @property
    def is_mixer_parameter(self):
        # type: () -> bool
        return self._is_mixer_parameter

    @classmethod
    def set_live_device_parameter(cls, param, value):
        # type: (Live.DeviceParameter.DeviceParameter, float) -> None
        if not param.is_enabled:
            return None
        value = max(param.min, value)
        value = min(param.max, value)
        # noinspection PyPropertyAccess
        param.value = value
