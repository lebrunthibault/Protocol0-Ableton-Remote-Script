from collections import deque
from functools import partial

from typing import Deque, Iterable, Union, Any, Optional, List, Type, Callable, cast

from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.backend.BackendResponseEvent import BackendResponseEvent
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import get_frame_info, nop, get_callable_repr
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.CallableWithCallbacks import CallableWithCallbacks
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.shared.sequence.SequenceStep import SequenceStep
from protocol0.shared.types import Func


class Sequence(SequenceStateMachineMixin):
    """
    Replacement of the _Framework Task.
    I added asynchronous behavior by hooking in the listener system and my own event system,
    including communication with the backend
    Encapsulates and composes all asynchronous tasks done in the script.
    """
    __subject_events__ = ("terminated",)
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

    def add(self, func=nop, name=None, notify_terminated=True):
        # type: (Union[Iterable, Callable, object], str, bool) -> Sequence
        """ callback can be a callable or a list of callable (will execute in parallel) """
        assert callable(func) or isinstance(func, Iterable), "You passed a non callable (%s) to %s" % (func, self)
        if isinstance(func, List):
            from protocol0.shared.sequence.ParallelSequence import ParallelSequence
            func = ParallelSequence(func).start

        func = cast(Callable, func)

        step_name = "%s : step %s" % (self.name, name or get_callable_repr(func))

        step = SequenceStep(func, step_name, notify_terminated)
        self._steps.append(step)

        return self

    def done(self):
        # type: () -> Sequence
        self.change_state(SequenceStateEnum.STARTED)
        self.RUNNING_SEQUENCES.append(self)
        self._execute_next_step()
        return self

    def _execute_next_step(self):
        # type: () -> None
        if not self.started:
            return
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self._DEBUG:
                Logger.debug("Executing %s : %s" % (self, self._current_step))
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

    @p0_subject_slot("terminated")
    def _step_terminated(self):
        # type: () -> None
        if self._DEBUG:
            Logger.info("step terminated : %s" % self._current_step)
        self._execute_next_step()

    @p0_subject_slot("errored")
    def _step_errored(self):
        # type: () -> None
        self._error()

    def _error(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.ERRORED)
        self.disconnect()
        if self._DEBUG:
            Logger.error("%s" % self, debug=False)

    @p0_subject_slot("cancelled")
    def _step_cancelled(self):
        # type: () -> None
        self._cancel()

    def _cancel(self):
        # type: () -> None
        if self.started:
            self.change_state(SequenceStateEnum.CANCELLED)
            Logger.warning("%s has been cancelled" % self)
            if self._current_step:
                self._current_step.cancel()
            self.disconnect()

    def _terminate(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.TERMINATED)

        self.res = self._current_step.res if self._current_step else None
        self.notify_terminated()  # type: ignore[attr-defined]
        self.disconnect()

    """ ACTIONS """

    def defer(self):
        # type: () -> Sequence
        return self.add(partial(Scheduler.defer, self._execute_next_step), notify_terminated=False)

    def wait(self, ticks):
        # type: (int) -> Sequence
        return self.add(partial(Scheduler.wait, ticks, self._execute_next_step), notify_terminated=False)

    def wait_bars(self, bars):
        # type: (float) -> None
        self.wait_beats(bars * SongFacade.signature_numerator())

    def wait_beats(self, beats):
        # type: (float) -> None
        self.add(partial(Scheduler.wait_beats, beats, self._execute_next_step), notify_terminated=False)

    def wait_for_listener(self, listener, timeout=True):
        # type: (Callable, bool) -> None
        assert CallableWithCallbacks.func_has_callback_queue(listener)
        listener = cast(CallableWithCallbacks, listener)
        if not timeout:
            self.add(partial(listener.add_callback, self._execute_next_step), notify_terminated=False)
        else:
            self._add_timeout_step(partial(listener.add_callback, self._execute_next_step),
                                   "wait_for_listener %s" % listener)

    def wait_for_event(self, event):
        # type: (Type[object]) -> None
        self.wait_for_events([event])

    def wait_for_events(self, events):
        # type: (List[Type[object]]) -> None
        def subscribe():
            # type: () -> None
            for event in events:
                DomainEventBus.subscribe(event, on_event)

        def on_event(_):
            # type: (object) -> None
            for event in events:
                DomainEventBus.un_subscribe(event, on_event)
            if self.started:
                self._execute_next_step()

        self._add_timeout_step(subscribe, "wait_for_events %s" % events)

    def _add_timeout_step(self, func, legend):
        # type: (Callable, str) -> None
        seconds = 50

        def cancel():
            # type: () -> None
            if self._current_step and self._current_step._callable == execute:
                self._cancel()
                Backend.client().show_warning("cancelling after %s seconds : %s on %s" % (seconds, self, legend))

        def execute():
            # type: () -> None
            Scheduler.wait_seconds(seconds, cancel)
            func()

        self.add(execute, notify_terminated=False)

    def prompt(self, question):
        # type: (str) -> None
        """ helper method for prompts """

        def on_response(res):
            # type: (bool) -> None
            if res:
                self._execute_next_step()
            else:
                self._cancel()

        self._execute_backend_step(partial(Backend.client().prompt, question), on_response)

    def select(self, question, options, vertical=True):
        # type: (str, List, bool) -> None
        """ helper method for selects """
        self._execute_backend_step(partial(Backend.client().select, question, options, vertical=vertical))

    def _execute_backend_step(self, func, on_response=None):
        # type: (Func, Optional[Func]) -> None
        self.add(func, notify_terminated=False)

        def on_event(event):
            # type: (BackendResponseEvent) -> None
            DomainEventBus.un_subscribe(BackendResponseEvent, on_event)
            if self.started:
                self.res = event.res
                if on_response:
                    on_response(self.res)
                else:
                    self._execute_next_step()

        DomainEventBus.subscribe(BackendResponseEvent, on_event)

    """ ACTIONS """

    def disconnect(self):
        # type: () -> None
        super(Sequence, self).disconnect()
        self._current_step = None
        try:
            self.RUNNING_SEQUENCES.remove(self)
        except ValueError:
            pass
