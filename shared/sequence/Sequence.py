from collections import deque
from functools import partial

from typing import Deque, Iterable, Union, Any, Optional, List, Type, Callable, cast

from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.backend.BackendResponseEvent import BackendResponseEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.event.HasEmitter import HasEmitter
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.debug import get_frame_info
from protocol0.domain.shared.utils.func import nop, get_callable_repr
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.ParallelSequence import ParallelSequence
from protocol0.shared.sequence.SequenceState import SequenceState
from protocol0.shared.sequence.SequenceStep import SequenceStep
from protocol0.shared.sequence.SequenceTransition import SequenceStateEnum
from protocol0.shared.types import Func


class Sequence(Observable):
    """
    Replacement of the _Framework Task.
    I added asynchronous behavior by hooking in my own event system,
    including communication with the backend
    Encapsulates and composes all asynchronous tasks done in the script.
    """

    RUNNING_SEQUENCES = []  # type: List[Sequence]
    _DEBUG = False
    _STEP_TIMEOUT = 50  # seconds

    def __init__(self, name=None):
        # type: (Optional[str]) -> None
        super(Sequence, self).__init__()

        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: Optional[SequenceStep]
        self.state = SequenceState()
        self.res = None  # type: Optional[Any]
        frame_info = get_frame_info(2)
        if name:
            self.name = name
        elif frame_info:
            self.name = "[seq %s.%s]" % (frame_info.class_name, frame_info.method_name)
        else:
            self.name = "Unknown"

    def __repr__(self, **k):
        # type: (Any) -> str
        return self.name

    def add(self, func=nop, name=None, notify_terminated=True):
        # type: (Union[Iterable, Callable, object], str, bool) -> Sequence
        """callback can be a callable or a list of callable (will execute in parallel)"""
        assert callable(func) or isinstance(
            func, Iterable
        ), "You passed a non callable (%s) to %s" % (func, self)
        if isinstance(func, List):
            func = ParallelSequence(func).start

        func = cast(Callable, func)

        step_name = "%s : step %s" % (self.name, name or get_callable_repr(func))

        step = SequenceStep(func, step_name, notify_terminated)
        self._steps.append(step)

        return self

    def done(self):
        # type: () -> Sequence
        self.state.change_to(SequenceStateEnum.STARTED)
        self.RUNNING_SEQUENCES.append(self)
        self._execute_next_step()
        return self

    def _execute_next_step(self):
        # type: () -> None
        if not self.state.started:
            return
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self._DEBUG:
                Logger.debug("%s : Executing %s" % (self, self._current_step))
            self._current_step.register_observer(self)
            self._current_step.start()
        else:
            self._terminate()

    @classmethod
    def reset(cls):
        # type: () -> None
        for seq in reversed(Sequence.RUNNING_SEQUENCES):
            seq._cancel()
        Sequence.RUNNING_SEQUENCES = []

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, SequenceStep):
            if observable.state.terminated:
                if self._DEBUG:
                    Logger.info("step terminated : %s" % self._current_step)
                self._execute_next_step()
            elif observable.state.errored:
                self._error()
            elif observable.state.cancelled:
                self._cancel()

            observable.remove_observer(self)

    def _error(self):
        # type: () -> None
        self.state.change_to(SequenceStateEnum.ERRORED)
        self.disconnect()
        if self._DEBUG:
            Logger.warning("Sequence errored : %s" % self)

    def _cancel(self):
        # type: () -> None
        if self.state.started:
            self.state.change_to(SequenceStateEnum.CANCELLED)
            Logger.warning("%s has been cancelled" % self)
            if self._current_step:
                self._current_step.cancel()
            self.disconnect()

    def _terminate(self):
        # type: () -> None
        self.state.change_to(SequenceStateEnum.TERMINATED)

        self.res = self._current_step.res if self._current_step else None
        self.notify_observers()
        self.disconnect()

    """ ACTIONS """

    def log(self, message):
        # type: (str) -> Sequence
        return self.add(lambda: Logger.warning(message))

    def defer(self):
        # type: () -> Sequence
        return self.add(partial(Scheduler.defer, self._execute_next_step), notify_terminated=False)

    def wait(self, ticks):
        # type: (int) -> Sequence
        return self.add(
            partial(Scheduler.wait, ticks, self._execute_next_step), notify_terminated=False
        )

    def wait_bars(self, bars, wait_for_song_start=False):
        # type: (float, bool) -> None
        if not SongFacade.is_playing() and wait_for_song_start:
            self.wait_for_event(SongStartedEvent)

        self.wait_beats(bars * SongFacade.signature_numerator())

    def wait_beats(self, beats):
        # type: (float) -> None
        def execute():
            # type: () -> None
            if not SongFacade.is_playing():
                Logger.warning("Cannot wait %s beats, song is not playing. %s" % (beats, self))
            else:
                Scheduler.wait_beats(beats, self._execute_next_step)

        self.add(execute, notify_terminated=False)

    def wait_for_event(self, event_class, expected_emitter=None, continue_on_song_stop=False):
        # type: (Type[object], object, bool) -> Sequence
        """
        Will continue the sequence after an event of type event_class is fired

        expected_emitter : passing an object here will check that the event was
        emitter from the right emitter before continuing the Sequence

        continue_on_song_stop: for events relying on a playing song, setting
        continue_on_song_stop to
        True
        will continue the sequence on a SongStoppedEvent
        """
        if expected_emitter is not None:
            assert issubclass(event_class, HasEmitter)

        def subscribe():
            # type: () -> None
            DomainEventBus.subscribe(event_class, on_event)
            if continue_on_song_stop:
                DomainEventBus.once(SongStoppedEvent, on_event)

        def on_event(event):
            # type: (object) -> None
            if expected_emitter is not None and isinstance(event, HasEmitter):
                if self._DEBUG:
                    Logger.info(
                        "expected emitter: %s, event.target(): %s"
                        % (expected_emitter, event.target())
                    )
                if event.target() != expected_emitter:
                    return  # not the right emitter

            DomainEventBus.un_subscribe(event_class, on_event)
            DomainEventBus.un_subscribe(SongStoppedEvent, on_event)
            if self.state.started:
                self._execute_next_step()

        self._add_timeout_step(subscribe, "wait_for_event %s" % event_class)
        return self

    def _add_timeout_step(self, func, legend):
        # type: (Callable, str) -> None
        seconds = self._STEP_TIMEOUT

        def cancel():
            # type: () -> None
            if self._current_step and self._current_step._callable == execute:
                self._cancel()
                Logger.warning("cancelling after %s seconds : %s on %s" % (seconds, self, legend))

        def execute():
            # type: () -> None
            Scheduler.wait_ms(seconds * 1000, cancel)
            func()

        self.add(execute, notify_terminated=False)

    def prompt(self, question):
        # type: (str) -> None
        """helper method for prompts"""

        def on_response(res):
            # type: (bool) -> None
            if res:
                self._execute_next_step()
            else:
                self._cancel()

        self._execute_backend_step(partial(Backend.client().prompt, question), on_response)

    def select(self, question, options, vertical=True):
        # type: (str, List, bool) -> None
        """helper method for selects"""
        self._execute_backend_step(
            partial(Backend.client().select, question, options, vertical=vertical)
        )

    def _execute_backend_step(self, func, on_response=None):
        # type: (Func, Optional[Func]) -> None
        self.add(func, notify_terminated=False)

        def on_event(event):
            # type: (BackendResponseEvent) -> None
            DomainEventBus.un_subscribe(BackendResponseEvent, on_event)
            if self.state.started:
                self.res = event.res
                if on_response:
                    on_response(self.res)
                else:
                    self._execute_next_step()

        DomainEventBus.subscribe(BackendResponseEvent, on_event)

    def disconnect(self):
        # type: () -> None
        self._current_step = None
        try:
            self.RUNNING_SEQUENCES.remove(self)
        except ValueError:
            pass
