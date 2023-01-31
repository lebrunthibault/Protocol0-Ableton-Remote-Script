import Live
from typing import Any, Optional

from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.shared.utils.timing import accelerate
from protocol0.domain.shared.utils.utils import clamp
from protocol0.shared.logging.Logger import Logger


class DeviceParameter(object):
    def __init__(self, device_parameter, enum=None):
        # type: (Live.DeviceParameter.DeviceParameter, Optional[DeviceParameterEnum]) -> None
        self._device_parameter = device_parameter  # type: Live.DeviceParameter.DeviceParameter
        self.device_name = ""

        try:
            if enum is not None:
                self.default_value = enum.default_value
            else:
                self.default_value = device_parameter.default_value
        except (RuntimeError, AttributeError):
            self.default_value = 0

    def __repr__(self, **k):
        # type: (Any) -> str
        return "%s: %s" % (self.name, self.value)

    @classmethod
    def create_from_name(cls, device_name, device_parameter):
        # type: (str, Live.DeviceParameter.DeviceParameter) -> DeviceParameter
        enum = DeviceParameterEnum.from_name(device_name, device_parameter.name)
        param = cls(device_parameter, enum=enum)
        param.device_name = device_name
        return param

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
            try:
                self._device_parameter.value = value
            except RuntimeError as e:
                Logger.warning(e)

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

    @classmethod
    def set_live_device_parameter(cls, param, value):
        # type: (Live.DeviceParameter.DeviceParameter, float) -> None
        if not param or not param.is_enabled:
            return None
        value = max(param.min, value)
        value = min(param.max, value)
        # noinspection PyPropertyAccess
        param.value = value

    @accelerate
    def scroll(self, go_next, factor=1):
        # type: (bool, int) -> None
        # using factor acceleration
        value_range = self.max - self.min
        step = (value_range / 1000)
        step *= factor
        value = self.value + step if go_next else self.value - step
        self.value = clamp(value, self.min, self.max)

    def reset(self):
        # type: () -> None
        if self.name == "Device On":
            # we define arbitrarily that toggling a device always starts from disabled state
            # not the opposite
            self.value = 0
        else:

            try:
                self.value = self.default_value
            except RuntimeError as e:
                Logger.error((e, self, self.device_name, self.min, self.max, self.default_value))
                raise e
