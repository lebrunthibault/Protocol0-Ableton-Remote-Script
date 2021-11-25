from abc import ABCMeta, abstractmethod

from typing import Optional

from protocol0.sequence.Sequence import Sequence


class AbstractValidator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_error_message(self):
        # type: () -> Optional[str]
        pass

    @abstractmethod
    def is_valid(self):
        # type: () -> bool
        pass

    def notify_valid(self):
        # type: () -> None
        pass

    @abstractmethod
    def fix(self):
        # type: () -> Optional[Sequence]
        pass
