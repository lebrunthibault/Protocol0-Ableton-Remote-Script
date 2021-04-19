from transitions import Machine, State

from a_protocol_0.enums.AbstractEnum import AbstractEnum


class SequenceState(AbstractEnum):
    UN_STARTED = "UN_STARTED"
    STARTED = "STARTED"
    TERMINATED = "TERMINATED"
    ERRORED = "ERRORED"


class SequenceStateMachineMixin(object):
    def __init__(self):
        # type: () -> None
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
        return self._state_machine.state.value

    @property
    def un_started(self):
        # type: () -> bool
        return self.state == SequenceState.UN_STARTED.value

    @property
    def started(self):
        # type: () -> bool
        return self.state == SequenceState.STARTED.value

    @property
    def errored(self):
        # type: () -> bool
        return self.state == SequenceState.ERRORED.value

    @property
    def terminated(self):
        # type: () -> bool
        return self.state == SequenceState.TERMINATED.value

    def dispatch(self, action):
        # type: (str) -> None
        self._state_machine.dispatch(action)

    def start(self):
        # type: () -> None
        self.dispatch("start")

    def terminate(self):
        # type: () -> None
        self.dispatch("terminate")
        # noinspection PyUnresolvedReferences
        self.notify_terminated()

    def error(self):
        # type: () -> None
        self.dispatch("error")
        # noinspection PyUnresolvedReferences
        self.notify_errored()

    def _on_start(self):
        # type: () -> None
        pass

    def _on_terminate(self):
        # type: () -> None
        pass
