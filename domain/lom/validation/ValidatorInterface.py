from abc import ABCMeta, abstractmethod

from typing import Optional

from protocol0.shared.sequence.Sequence import Sequence


class ValidatorInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_valid(self):
        # type: () -> bool
        raise NotImplementedError

    @abstractmethod
    def get_error_message(self):
        # type: () -> Optional[str]
        raise NotImplementedError

    @abstractmethod
    def fix(self):
        # type: () -> Optional[Sequence]
        raise NotImplementedError
