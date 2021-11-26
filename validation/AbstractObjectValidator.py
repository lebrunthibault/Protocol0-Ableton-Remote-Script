from protocol0.lom.AbstractObject import AbstractObject
from protocol0.utils.log import log_ableton
from protocol0.validation.AbstractValidator import AbstractValidator


class AbstractObjectValidator(AbstractValidator):
    def __init__(self, _, log):
        # type: (AbstractObject, bool) -> None
        self._log = log

    def log(self, message):
        # type: (str) -> None
        if self._log:
            log_ableton(message)
