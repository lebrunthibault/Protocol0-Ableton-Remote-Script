from typing import Any, Optional

from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.shared.utils import is_method


class PropertyNotNullValidator(ValidatorInterface):
    def __init__(self, obj, attribute):
        # type: (Any, str) -> None
        self._obj = obj
        self._attr = attribute

    def get_error_message(self):
        # type: () -> Optional[str]
        if self.is_valid():
            return None
        if not hasattr(self._obj, self._attr):
            return "%s has no attribute %s" % (self._obj, self._attr)
        else:
            return "Expected %s.%s to be not None" % (self._obj, self._attr)

    def is_valid(self):
        # type: () -> bool
        try:
            attribute = getattr(self._obj, self._attr)
            if is_method(attribute):
                return attribute() is not None
            else:
                return attribute is not None
        except AttributeError:
            return False

    def fix(self):
        # type: () -> None
        pass
