from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.sequence.SequenceTransition import SequenceTransition, SequenceStateEnum


class SequenceState(object):
    def __init__(self):
        # type: () -> None
        terminated_state = SequenceTransition(SequenceStateEnum.TERMINATED, [])
        cancelled_state = SequenceTransition(SequenceStateEnum.CANCELLED, [])
        errored_state = SequenceTransition(SequenceStateEnum.ERRORED, [])
        started_state = SequenceTransition(
            SequenceStateEnum.STARTED, [terminated_state, cancelled_state, errored_state]
        )
        un_started_state = SequenceTransition(SequenceStateEnum.UN_STARTED, [started_state])

        self.state = un_started_state
        self.res = None

    def change_to(self, enum):
        # type: (SequenceStateEnum) -> None
        new_state = self.state.get_transition(enum)
        if new_state is None:
            raise Protocol0Error(
                "Cannot change state from %s to %s : %s" % (self.state.enum, enum, self)
            )

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
