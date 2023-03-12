from typing import Any, Optional

from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.utils import compare_values
from protocol0.shared.logging.Logger import Logger


class PropertyValueValidator(ValidatorInterface):
    def __init__(self, obj, attribute, expected_value, name=None, fix=True):
        # type: (Any, str, Any, Optional[str], bool) -> None
        self._obj = obj
        self._attr = attribute
        self._expected_value = expected_value
        self._name = name
        self._fix = fix

    def get_error_message(self):
        # type: () -> Optional[str]
        if self.is_valid():
            return None
        if hasattr(self._obj, self._attr):
            error = "Got %s" % getattr(self._obj, self._attr)
        else:
            error = "%s has no attribute %s" % (self._obj, self._attr)
        name_prefix = "%s : " % self._name if self._name else ""
        return "%sExpected %s.%s to be %s. %s" % (
            name_prefix,
            self._obj,
            self._attr,
            self._expected_value,
            error,
        )

    def is_valid(self):
        # type: () -> bool
        try:
            return compare_values(getattr(self._obj, self._attr), self._expected_value)
        except AttributeError:
            return False

    def fix(self):
        # type: () -> None
        if not self._fix:
            return
        if hasattr(self._obj, self._attr):
            # try:
            setattr(self._obj, self._attr, self._expected_value)
            # except AttributeError as e:
            #     Logger.error("Fix error on %s - %s : %s" % (self._obj, self._attr, e))
        else:
            raise Protocol0Error("Cannot set attribute when it does not exist")
