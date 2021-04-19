from transitions import Machine, State
from typing import Any

from a_protocol_0.enums.AbstractEnum import AbstractEnum


class SequenceState(AbstractEnum):
    UN_STARTED = "UN_STARTED"
    STARTED = "STARTED"
    TERMINATED = "TERMINATED"
    ERRORED = "ERRORED"


class SequenceStateMachineMixin(object):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        transitions = [
            ["start", SequenceState.UN_STARTED, SequenceState.STARTED],
            ["terminate", SequenceState.STARTED, SequenceState.TERMINATED],
            ["error", SequenceState.STARTED, SequenceState.ERRORED],
        ]

        states = [
            State(SequenceState.UN_STARTED),
            State(SequenceState.STARTED, on_enter=[self._on_start]),
            State(SequenceState.TERMINATED, on_enter=[self._on_terminate]),
            State(SequenceState.ERRORED, on_enter=[self._on_terminate]),
        ]

        self._state_machine = Machine(states=states, transitions=transitions, initial=SequenceState.UN_STARTED)

    @property
    def state(self):
        # type: () -> str
        return str(self._state_machine.state)

    @property
    def un_started(self):
        # type: () -> bool
        return self.state == str(SequenceState.UN_STARTED)

    @property
    def started(self):
        # type: () -> bool
        return self.state == str(SequenceState.STARTED)

    @property
    def errored(self):
        # type: () -> bool
        return self.state == str(SequenceState.ERRORED)

    @property
    def terminated(self):
        # type: () -> bool
        return self.state == str(SequenceState.TERMINATED)

    def dispatch(self, action):
        # type: (str) -> None
        self._state_machine.dispatch(action)

    def start(self):
        # type: () -> None
        self.dispatch("start")

    def terminate(self):
        # type: () -> None
        self.dispatch("terminate")
        self.notify_terminated()  # type: ignore[attr-defined]

    def error(self):
        # type: () -> None
        self.dispatch("error")
        self.notify_errored()  # type: ignore[attr-defined]

    def _on_start(self):
        # type: () -> None
        pass

    def _on_terminate(self):
        # type: () -> None
        pass
