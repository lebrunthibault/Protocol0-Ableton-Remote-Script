from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.sequence.SequenceState import SequenceState, SequenceStateEnum


class SequenceStateMachineMixin(object):
    def __init__(self):
        # type: () -> None
        terminated_state = SequenceState(SequenceStateEnum.TERMINATED, [])
        cancelled_state = SequenceState(SequenceStateEnum.CANCELLED, [])
        errored_state = SequenceState(SequenceStateEnum.ERRORED, [])
        started_state = SequenceState(SequenceStateEnum.STARTED, [terminated_state, cancelled_state, errored_state])
        un_started_state = SequenceState(SequenceStateEnum.UN_STARTED, [started_state])

        self.state = un_started_state

    def change_state(self, enum):
        # type: (SequenceStateEnum) -> None
        new_state = self.state.get_transition(enum)
        if new_state is None:
            raise Protocol0Error("Cannot change state from %s to %s" % (self.state.enum, enum))

        self.state = new_state

    @property
    def started(self):
        # type: () -> bool
        return self.state.enum == SequenceStateEnum.STARTED

    @property
    def errored(self):
        # type: () -> bool
        return self.state.enum == SequenceStateEnum.ERRORED

    @property
    def cancelled(self):
        # type: () -> bool
        return self.state.enum == SequenceStateEnum.CANCELLED

    @property
    def terminated(self):
        # type: () -> bool
        return self.state.enum == SequenceStateEnum.TERMINATED
