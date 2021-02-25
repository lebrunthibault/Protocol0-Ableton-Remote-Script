from enum import Enum
from typing import TYPE_CHECKING

from a_protocol_0.errors.Protocol0Error import Protocol0Error

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip.Clip import Clip


class AutomationRampMode(Enum):
    NO_RAMP = ""
    END_RAMP = "*"
    LINEAR_RAMP = "/"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def get_from_value(cls, value):
        value = value.strip()
        if not value:
            return AutomationRampMode.NO_RAMP
        if not AutomationRampMode.has_value(value):
            raise Protocol0Error("Invalid ramp mode value: '%s'" % value)
        return AutomationRampMode(value)


class AutomationRamp(object):
    def __init__(self, ramp_mode=AutomationRampMode.NO_RAMP, time_division=1):
        # type: (AutomationRampMode, int) -> None
        self.ramp_mode = ramp_mode
        self.division = time_division  # allows configuring the interval of the AutomationRampMode.END_RAMP

    @staticmethod
    def make(value):
        # type (str) -> AutomationRamp
        chars = list(set(value))
        if len(chars) > 1:
            raise Protocol0Error("Invalid ramp mode value: '%s'" % value)
        if len(chars) == 0:
            return AutomationRamp(AutomationRampMode.NO_RAMP, 1)

        return AutomationRamp(AutomationRampMode.get_from_value(chars[0]), len(value))