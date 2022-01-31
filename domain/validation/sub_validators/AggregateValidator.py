from typing import Optional, List

from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.validation.ValidatorInterface import ValidatorInterface


class AggregateValidator(ValidatorInterface):
    def __init__(self, validators):
        # type: (List[ValidatorInterface]) -> None
        self._validators = validators

    def get_error_message(self):
        # type: () -> Optional[str]
        error_messages = filter(None, [validator.get_error_message() for validator in self._validators])
        if len(error_messages) == 0:
            return None
        else:
            return "\n".join(error_messages)

    def is_valid(self):
        # type: () -> bool
        return all(validator.is_valid() for validator in self._validators)

    def fix(self):
        # type: () -> Sequence
        seq = Sequence()
        for validator in self._validators:
            if not validator.is_valid():
                seq.add(validator.fix)
        return seq.done()
