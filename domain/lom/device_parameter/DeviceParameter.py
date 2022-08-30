import Live
from typing import Any, Optional

from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.shared.logging.Logger import Logger


class DeviceParameter(object):
    def __init__(self, device_parameter, enum=None, is_mixer_parameter=False):
        # type: (Live.DeviceParameter.DeviceParameter, Optional[DeviceParameterEnum], bool) -> None
        self._device_parameter = device_parameter  # type: Live.DeviceParameter.DeviceParameter
        self._is_mixer_parameter = is_mixer_parameter
        self.device_name = ""

        try:
            if enum is not None:
                self._default_value = enum.default_value
            else:
                self._default_value = 1
                self._default_value = device_parameter.default_value
        except (RuntimeError, AttributeError):
            self._default_value = 0

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
            self._device_parameter.value = value

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

    def touch(self, value):
        # type:(Any) -> None
        """
            Modify the parameter the most slightly possible
            so as to have live record the value as the base one if the automation stops
            This is a solution to the partial automation problem in session view
            When preparing clip automation on start, touching the parameter at the very end of the clip
            will make live stay on the value instead of folding back to an old value
        """
        # only for continuous parameters
        if self.is_quantized:
            return None

        # sets the value or a slightly different one if it's the same
        if value == self.value:
            increment = 0.001
            if value == self.max:
                value -= increment
            else:
                value = min(self.max, value + increment)

        self.value = value

    def reset(self):
        # type: () -> None
        if self.name == "Device On":
            # we define arbitrarily that toggling a device always starts from disabled state
            # not the opposite
            self.value = 0
        else:
            try:
                self.value = self._default_value
            except RuntimeError as e:
                Logger.error((e, self, self.device_name, self.min, self.max, self._default_value))
                raise e
