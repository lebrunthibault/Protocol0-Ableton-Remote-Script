from collections import deque
from functools import partial

from typing import Deque, Optional, Iterable, Union, Callable, Any, List

from protocol0.application.config import Config
from protocol0.domain.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.domain.sequence.SequenceStep import SequenceStep
from protocol0.domain.shared.SongFacade import SongFacade
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.utils import get_frame_info, nop
from protocol0.infra.System import System
from protocol0.shared.Logger import Logger


class Sequence(SequenceStateMachineMixin):
    """
    Replacement of the _Framework Task as it does not seem to allow variable timeouts like triggers from listeners.
    Encapsulates and composes all asynchronous tasks done in the script.
    """
    RUNNING_SEQUENCES = []  # type: List[Sequence]

    def __init__(self):
        # type: () -> None
        super(Sequence, self).__init__()

        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: Optional[SequenceStep]
        self._on_end = None  # type: Optional[Callable]
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

    @property
    def debug_str(self):
        # type: () -> str
        message = "%s in state %s" % (self, self.state)
        if not self._current_step:
            message += " (empty seq)"
        if self.res:
            message += " (res %s)" % self.res
        return message

    @property
    def waiting_for_system(self):
        # type: () -> bool
        return self._current_step is not None and self._current_step.wait_for_system

    def _on_start(self):
        # type: () -> None
        self.RUNNING_SEQUENCES.append(self)
        self._execute_next_step()

    def _execute_next_step(self):
        # type: () -> None
        if self.has_final_state:
            return
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if Config.SEQUENCE_DEBUG:
                Logger.log_debug("%s : %s" % (self, self._current_step), debug=False)
            self._step_terminated.subject = self._current_step
            self._step_errored.subject = self._current_step
            self._step_cancelled.subject = self._current_step
            self._current_step.start()
        else:
            self.terminate()

    def on_system_response(self, res):
        # type: (bool) -> None
        if res:
            self.res = res  # system response is accessible from the next step
            self._execute_next_step()
            return None

        if self._current_step.no_cancel:
            self.terminate()
        else:
            self.cancel()

    @p0_subject_slot("terminated")
    def _step_terminated(self):
        # type: () -> None
        if self._current_step and self._current_step.wait_for_system:
            # allowing only one running sequence to wait for system response
            for seq in Sequence.RUNNING_SEQUENCES:
                if seq.waiting_for_system and seq != self:
                    seq.terminate()
            return None  # waiting for system response
        self._execute_next_step()

    @p0_subject_slot("errored")
    def _step_errored(self):
        # type: () -> None
        self.error()

    @p0_subject_slot("cancelled")
    def _step_cancelled(self):
        # type: () -> None
        self.cancel()

    def _on_final_step(self):
        # type: () -> None
        if self._on_end:
            self._on_end()
        try:
            self.RUNNING_SEQUENCES.remove(self)
        except ValueError:
            pass

    def _on_cancel(self):
        # type: () -> None
        self._on_final_step()

    def _on_terminate(self):
        # type: () -> None
        self._on_final_step()

        self.res = self._current_step.res if self._current_step else None
        self._current_step = None

        if self.errored and Config.SEQUENCE_DEBUG:
            Logger.log_error(self.debug_str, debug=False)

    def add(  # type: ignore[no-untyped-def]
            self,
            func=nop,  # type: Union[Iterable, Callable, object]
            name=None,  # type: str
            wait=0,  # type: int
            wait_beats=0,  # type: float
            wait_bars=0,  # type: float
            wait_for_system=False,  # type: bool
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
        assert not self.has_final_state
        # assert not isinstance(func, Sequence), "You passed a Sequence object instead of a Sequence factory to add"

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
                no_cancel=no_cancel,
                complete_on=complete_on,
                check_timeout=0 if no_timeout else 4,
                # check_timeout is the number of (exponential duration) checks executed before step failure (based on the Live.Base.Timer tick)
            )
        )

        return self

    def on_end(self, func):
        # type: (Callable) -> None
        self._on_end = func

    def prompt(self, question, *a, **k):
        # type: (str, Any, Any) -> None
        """ helper method for prompts """
        self.add(partial(System.get_instance().prompt, question), wait_for_system=True, *a, **k)

    def select(self, question, options, vertical=True, *a, **k):
        # type: (str, List[str], bool, Any, Any) -> None
        """ helper method for selects """
        self.add(partial(System.get_instance().select, question, options, vertical=vertical), wait_for_system=True, *a, **k)

    def done(self):
        # type: () -> Sequence
        self.start()
        return self
