from transitions import Machine, State

from a_protocol_0.enums.AbstractEnum import AbstractEnum


class SequenceState(AbstractEnum):
    UN_STARTED = "UN_STARTED"
    STARTED = "STARTED"
    TERMINATED = "TERMINATED"
    ERRORED = "ERRORED"


class SequenceStateMachineMixin(object):
    def __init__(self, *a, **k):
        super(SequenceStateMachineMixin, self).__init__(*a, **k)
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

    def terminate(self):
        self.dispatch("terminate")
        # noinspection PyUnresolvedReferences
        self.notify_terminated()

    def error(self):
        self.dispatch("error")

    def _on_start(self):
        pass

    def _on_terminate(self):
        pass
