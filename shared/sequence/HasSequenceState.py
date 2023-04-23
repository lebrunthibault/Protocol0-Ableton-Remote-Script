from typing_extensions import Protocol, runtime_checkable
from typing import Any

from protocol0.shared.observer.Observer import Observer
from protocol0.shared.sequence.SequenceState import SequenceState


@runtime_checkable
class HasSequenceState(Protocol):
    @property
    def state(self):
        # type: () -> SequenceState
        raise NotImplementedError

    @property
    def res(self):
        # type: () -> Any
        raise NotImplementedError

    def register_observer(self, observer):
        # type: (Observer) -> None
        raise NotImplementedError

    def remove_observer(self, observer):
        # type: (Observer) -> None
        raise NotImplementedError
