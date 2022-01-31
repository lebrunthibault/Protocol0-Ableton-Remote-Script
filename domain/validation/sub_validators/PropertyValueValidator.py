from typing import Any, Optional

from protocol0.domain.errors.Protocol0Error import Protocol0Error
from protocol0.domain.utils import compare_values
from protocol0.domain.validation.ValidatorInterface import ValidatorInterface


class PropertyValueValidator(ValidatorInterface):
    def __init__(self, obj, attribute, expected_value):
        # type: (Any, str, Any) -> None
        self._obj = obj
        self._attr = attribute
        self._expected_value = expected_value

    def get_error_message(self):
        # type: () -> Optional[str]
        if self.is_valid():
            return None
        if hasattr(self._obj, self._attr):
            error = "Got %s" % getattr(self._obj, self._attr)
        else:
            error = "Object has no attribute %s" % self._attr
        return "Expected %s.%s to be %s. %s" % (self._obj, self._attr, self._expected_value, error)

    def is_valid(self):
        # type: () -> bool
        try:
            return compare_values(getattr(self._obj, self._attr), self._expected_value)
        except AttributeError:
            return False

    def fix(self):
        # type: () -> None
        if hasattr(self._obj, self._attr):
            setattr(self._obj, self._attr, self._expected_value)
        else:
            raise Protocol0Error("Cannot set attribute when it does not exist")
