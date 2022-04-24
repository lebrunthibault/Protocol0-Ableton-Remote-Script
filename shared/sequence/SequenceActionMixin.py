from functools import partial

from typing import Optional, List, Type, TYPE_CHECKING, Callable, cast

from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.backend.BackendResponseEvent import BackendResponseEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.CallableWithCallbacks import CallableWithCallbacks
from protocol0.shared.types import Func

if TYPE_CHECKING:
    from protocol0.shared.sequence.Sequence import Sequence


# noinspection PyTypeHints
class SequenceActionMixin(object):
    def defer(self):
        # type: (Sequence) -> Sequence
        return self.add(partial(Scheduler.defer, self._execute_next_step), notify_terminated=False)

    def wait(self, ticks):
        # type: (Sequence, int) -> Sequence
        return self.add(partial(Scheduler.wait, ticks, self._execute_next_step), notify_terminated=False)

    def wait_bars(self, bars):
        # type: (Sequence, float) -> None
        self.wait_beats(bars * SongFacade.signature_numerator())

    def wait_beats(self, beats):
        # type: (Sequence, float) -> None
        self.add(partial(Scheduler.wait_beats, beats, self._execute_next_step), notify_terminated=False)

    def wait_for_listener(self, listener, timeout=True):
        # type: (Sequence, Callable, bool) -> None
        assert CallableWithCallbacks.func_has_callback_queue(listener)
        listener = cast(CallableWithCallbacks, listener)
        if not timeout:
            self.add(partial(listener.add_callback, self._execute_next_step), notify_terminated=False)
        else:
            self._add_timeout_step(partial(listener.add_callback, self._execute_next_step), "wait_for_listener %s" % listener)

    def wait_for_event(self, event):
        # type: (Sequence, Type[object]) -> None
        self.wait_for_events([event])

    def wait_for_events(self, events):
        # type: (Sequence, List[Type[object]]) -> None
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
        # type: (Sequence, Callable, str) -> None
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
        # type: (Sequence, str) -> None
        """ helper method for prompts """

        def on_response(res):
            # type: (bool) -> None
            if res:
                self._execute_next_step()
            else:
                self._cancel()

        self._execute_backend_step(partial(Backend.client().prompt, question), on_response)

    def select(self, question, options, vertical=True):
        # type: (Sequence, str, List, bool) -> None
        """ helper method for selects """
        self._execute_backend_step(partial(Backend.client().select, question, options, vertical=vertical))

    def _execute_backend_step(self, func, on_response=None):
        # type: (Sequence, Func, Optional[Func]) -> None
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
