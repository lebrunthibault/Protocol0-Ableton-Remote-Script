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
        # type: (Sequence) -> None
        self.add(partial(Scheduler.defer, self._execute_next_step), no_terminate=True)

    def wait(self, ticks):
        # type: (Sequence, int) -> None
        self.add(partial(Scheduler.wait, ticks, self._execute_next_step), no_terminate=True)

    def wait_bars(self, bars):
        # type: (Sequence, float) -> None
        self.wait_beats(bars * SongFacade.signature_numerator())

    def wait_beats(self, beats):
        # type: (Sequence, float) -> None
        self.add(partial(Scheduler.wait_beats, beats, self._execute_next_step), no_terminate=True)

    def wait_for_listener(self, listener):
        # type: (Sequence, Callable) -> None
        assert CallableWithCallbacks.func_has_callback_queue(listener)
        listener = cast(CallableWithCallbacks, listener)
        print("got listener %s" % listener)
        # NB : we could add a timeout here
        # listener.add_callback(self._execute_next_step)

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

        self.add(subscribe, no_terminate=True)

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
        self.add(func, no_terminate=True)

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
