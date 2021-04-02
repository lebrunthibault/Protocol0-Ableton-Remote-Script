from abc import abstractmethod

from transitions import Machine, State

from a_protocol_0.sequence.SequenceState import SequenceState


class SequenceStateMachineMixin():
    def __init__(self, *a, **k):
        raise "hello"
        transitions = [
            ['start', SequenceState.UN_STARTED, SequenceState.STARTED],
            ['terminate', SequenceState.STARTED, SequenceState.TERMINATED],
            ['error', SequenceState.STARTED, SequenceState.ERRORED]
        ]

        states = [
            State(SequenceState.UN_STARTED),
            State(SequenceState.STARTED, on_enter=[self._on_start]),
            State(SequenceState.TERMINATED, on_enter=[self._on_terminate]),
            State(SequenceState.ERRORED, on_enter=[self._on_terminate]),
        ]

        self._state_machine = Machine(states=states, transitions=transitions,
                                      initial=SequenceState.UN_STARTED)

    @property
    def state(self):
        return self._state_machine.state

    @property
    def started(self):
        # type: () -> SequenceState
        return self._state_machine.state == SequenceState.STARTED

    @property
    def errored(self):
        # type: () -> SequenceState
        return self._state_machine.state == SequenceState.ERRORED

    @property
    def terminated(self):
        # type: () -> SequenceState
        return self._state_machine.state == SequenceState.TERMINATED

    def dispatch(self, action):
        # type: (str) -> None
        self._state_machine.dispatch(action)

    def start(self):
        self.dispatch("start")

    @abstractmethod
    def _on_start(self):
        raise NotImplementedError

    @abstractmethod
    def _on_terminate(self):
        raise NotImplementedError