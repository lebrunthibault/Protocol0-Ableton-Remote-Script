from typing import Optional, List

from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.AbstractEnum import AbstractEnum


class SequenceStateEnum(AbstractEnum):
    UN_STARTED = "UN_STARTED"
    STARTED = "STARTED"
    TERMINATED = "TERMINATED"
    CANCELLED = "CANCELLED"
    ERRORED = "ERRORED"


class SequenceTransition(object):
    def __init__(self, enum, allowed_transitions):
        # type: (SequenceStateEnum, List[SequenceTransition]) -> None
        self.enum = enum
        self._allowed_transitions = allowed_transitions

    def __repr__(self):
        # type: () -> str
        return self.enum.name

    def get_transition(self, new_state_enum):
        # type: (SequenceStateEnum) -> Optional["SequenceTransition"]
        return find_if(lambda s: s.enum == new_state_enum, self._allowed_transitions)
