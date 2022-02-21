from collections import deque
from functools import partial

from typing import Deque, Optional, Iterable, Union, Callable, Any, List, Type

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.System import System
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.utils import get_frame_info, nop
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.shared.sequence.SequenceStep import SequenceStep


class Sequence(UseFrameworkEvents, SequenceStateMachineMixin):
    __subject_events__ = ("terminated",)
    """
    Replacement of the _Framework Task as it does not seem to allow variable timeouts like triggers from listeners.
    Encapsulates and composes all asynchronous tasks done in the script.
    """
    RUNNING_SEQUENCES = []  # type: List[Sequence]
    _DEBUG = False

    def __init__(self):
        # type: () -> None
        super(Sequence, self).__init__()

        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: Optional[SequenceStep]
        self.res = None  # type: Optional[Any]
        frame_info = get_frame_info(2)
        if frame_info:
            self.name = "[seq %s.%s]" % (frame_info.class_name, frame_info.method_name)
        else:
            self.name = "Unknown"

    def __repr__(self, **k):
        # type: (Any) -> str
        return self.name

    def __call__(self):
        # type: () -> Sequence
        return self.done()

    def add(  # type: ignore[no-untyped-def]
            self,
            func=nop,  # type: Union[Iterable, Callable, object]
            name=None,  # type: str
            wait=0,  # type: int
            wait_beats=0,  # type: float
            wait_bars=0,  # type: float
            wait_for_system=False,  # type: bool
            wait_for_event=None,  # type: Type[object]
            wait_for_events=None,  # type: List[Type[object]]
            no_cancel=False,  # type: bool
            complete_on=None,  # type: Callable
            no_timeout=False,  # type: bool
    ):
        """
        callback can be :
        - not given (nop): can be used to just wait on a condition (with complete_on)
        - a callable or a list of callable (parallel sequence execution) which are added as a single SequenceStep
        """
        assert callable(func) or isinstance(func, Iterable), "You passed a non callable (%s) to %s" % (
            func,
            self,
        )
        assert not (wait_for_event and wait_for_events), "You used both wait_for_event and wait_for_events"
        if wait_for_events:
            assert isinstance(wait_for_events, List), "wait_for_events should be a List"
        else:
            wait_for_events = []

        if wait_for_event:
            wait_for_events = [wait_for_event]

        if wait_bars:
            wait_beats += wait_bars * SongFacade.signature_numerator()
        self._steps.append(
            SequenceStep.make(
                self,
                func,
                name=name,
                wait=wait,
                wait_beats=wait_beats,
                wait_for_system=wait_for_system,
                wait_for_events=wait_for_events,
                no_cancel=no_cancel,
                complete_on=complete_on,
                check_timeout=0 if no_timeout else 4,
                # check_timeout is the number of (exponential duration) checks executed before step failure (based on the Live.Base.Timer tick)
            )
        )

        return self

    def prompt(self, question, no_cancel=False):
        # type: (str, bool) -> None
        """ helper method for prompts """
        self.add(partial(System.client().prompt, question), wait_for_system=True, no_cancel=no_cancel)

    def select(self, question, options, vertical=True):
        # type: (str, List[str], bool) -> None
        """ helper method for selects """
        self.add(partial(System.client().select, question, options, vertical=vertical), wait_for_system=True)

    def done(self):
        # type: () -> Sequence
        self.start()
        return self

    @property
    def waiting_for_system(self):
        # type: () -> bool
        return self._current_step is not None and self._current_step.wait_for_system

    def start(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.STARTED)
        self.RUNNING_SEQUENCES.append(self)
        self._execute_next_step()

    def _execute_next_step(self):
        # type: () -> None
        if self.errored or self.cancelled or self.terminated:
            return
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self._DEBUG:
                Logger.log_debug("%s : %s" % (self, self._current_step))
            self._step_terminated.subject = self._current_step
            self._step_errored.subject = self._current_step
            self._step_cancelled.subject = self._current_step
            self._current_step.start()
        else:
            self._terminate()

    @classmethod
    def restart(cls):
        # type: () -> None
        for seq in reversed(Sequence.RUNNING_SEQUENCES):
            seq._cancel()
        Sequence.RUNNING_SEQUENCES = []

    @classmethod
    def handle_system_response(cls, res):
        # type: (Any) -> None
        waiting_sequence = next((seq for seq in Sequence.RUNNING_SEQUENCES if
                                 seq._current_step is not None and seq._current_step.wait_for_system
                                 ), None)
        if waiting_sequence is None:
            Logger.log_info("Response (%s) received from system but couldn't find a waiting sequence" % res)
            return

        waiting_sequence.on_system_response(res=res)

    def on_system_response(self, res):
        # type: (bool) -> None
        if res:
            self.res = res  # system response is accessible from the next step
            self._execute_next_step()
            return None

        if self._current_step.no_cancel:
            self._terminate()
        else:
            self._cancel()

    @p0_subject_slot("terminated")
    def _step_terminated(self):
        # type: () -> None
        if self._DEBUG:
            Logger.log_info("step terminated : %s" % self._current_step)
        self._execute_next_step()

    @p0_subject_slot("errored")
    def _step_errored(self):
        # type: () -> None
        self._error()

    def _error(self, message=None):
        # type: (Optional[str]) -> None
        if message:
            Logger.log_error(message)
        self.change_state(SequenceStateEnum.ERRORED)
        self.disconnect()
        if self._DEBUG:
            Logger.log_error("%s" % self, debug=False)

    @p0_subject_slot("cancelled")
    def _step_cancelled(self):
        # type: () -> None
        self._cancel(notify_step=False)

    def _cancel(self, notify_step=True):
        # type: (bool) -> None
        if self.errored:
            return
        self.change_state(SequenceStateEnum.CANCELLED)
        if notify_step and self._current_step:
            self._current_step.cancel(notify=False)
        self.disconnect()

    def _terminate(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.TERMINATED)

        self.res = self._current_step.res if self._current_step else None
        self.notify_terminated()  # type: ignore[attr-defined]
        self.disconnect()

    def disconnect(self):
        # type: () -> None
        super(Sequence, self).disconnect()
        if self._current_step:
            self._current_step.waiting_for_system = False
            self._current_step = None
        try:
            self.RUNNING_SEQUENCES.remove(self)
        except ValueError:
            pass
