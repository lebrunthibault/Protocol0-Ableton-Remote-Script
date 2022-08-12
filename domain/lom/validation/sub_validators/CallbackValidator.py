from typing import Any, Optional, Callable

from protocol0.shared.sequence.Sequence import Sequence
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface


class CallbackValidator(ValidatorInterface):
    def __init__(self, obj, callback_validator, callback_fixer=None, error_message=None):
        # type: (Any, Callable, Optional[Callable], Optional[str]) -> None
        self._obj = obj
        self._callback_validator = callback_validator
        self._callback_fixer = callback_fixer
        self._error_message = error_message

    def get_error_message(self):
        # type: () -> Optional[str]
        if self.is_valid():
            return None
        else:
            return self._error_message or "callback failed for %s" % self._obj

    def is_valid(self):
        # type: () -> bool
        return self._callback_validator(self._obj)

    def fix(self):
        # type: () -> Optional[Sequence]
        if self._callback_fixer is not None:
            return self._callback_fixer(self._obj)
        else:
            return None
