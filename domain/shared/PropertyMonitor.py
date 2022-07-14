from typing import Optional, Callable

from protocol0.domain.shared.LiveObject import LiveObject
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.decorators import defer


class PropertyMonitor(object):
    def __init__(self, obj, property_name, allowed_value_validator, label=None):
        # type: (LiveObject, str, Callable, Optional[str]) -> None
        self._obj = obj
        self._property_name = property_name
        self._allowed_value_validator = allowed_value_validator
        self._label = label or "%s.%s" % (self._obj, self._property_name)
        listener_func_name = "add_%s_listener" % self._property_name
        getattr(self._obj, listener_func_name)(lambda: self._listener())

    def __repr__(self):
        # type: () -> str
        return self._label

    @defer
    def _listener(self):
        # type: () -> None
        current_value = getattr(self._obj, self._property_name)
        if not self._allowed_value_validator(current_value):
            Backend.client().show_warning(
                "Unexpected value change for %s : %s" % (self, current_value)
            )
