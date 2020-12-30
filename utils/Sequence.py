import time
from collections import deque, Iterable
from typing import List, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.SequenceStep import SequenceStep
from a_protocol_0.utils.utils import get_frame_info, nop

UN_STARTED = 0
STARTED = 1
TERMINATED = 2


class Sequence(AbstractControlSurfaceComponent):
    __subject_events__ = ('terminated',)

    """
        Replacement of the _Framework Task as it does not seem to allow variable timeouts like triggers from listeners.
            Nothing but some pale asyncio imitation. Can't wait for python3
        A Sequence represents a function and a SequenceStep represents one or multiple statement
        A Sequence step can very often be a function call and is thus a Sequence as well.
        Sequences can be nested allowing deep asynchronous function calls.
        A Sequence should never be passed to the called code but instead the called code should return it's own sequence to be appended to the calling one.
            Attention : this means that the called code is gonna be called synchronously, any data lookup (e.g. on Live API)
                is gonna be computed at sequence instantiation time and not at sequence runtime !
                If you don't want this behavior to happen, wrap your lookup calls in a step
                Ideally, an asynchronous method should wrap all it's statements in a sequence and do lookups in lambda functions
        The code can declare asynchronous behavior in 2 ways:
            - via interval which leverages Live 100ms tick for short and hard to check tasks like click on the interface
            - via the on_complete argument that defers the completion of the step until a condition is satisfied
        This condition can be either
            - a simple callable returning a bool : in this case an exponential polling is setup with a timeout
            - a CallbackDescriptor decorated function : the step executes when the function is called next.
            This is the best part because it allows us to react to the execution of Live listeners (e.g. on_selected_track_changed)
            or even our own listeners. Thus being a shortcut to define yet another listener on an already listened to subject.
        A sequence step should always define it's completion step and not expect the next step to handle any timeout or checks
            Example : A step song.create_midi_track should define it's completion check to be the next call to the _added_track_listener.
            Like this any step can always be assured that it executes after the previous one has succeeded or failed (thus ending the sequence).
        sync allows the async methods to be called both synchronously and asynchronously.
            - In the first case the caller expects immediate action or is not even aware of the sequence pattern and sync is True
            - In the second case the caller is going to nest the sequence to it's own and will call it later
        The bypass parameter is like an if for a sequence and finishes the sequence early.
            It's an implementation of the basic
            if a:
                return
            where a is the step and the enclosing function the sequence.
    """

    def __init__(self, steps=[], interval=0, debug=True, name=None, sync=False, *a, **k):
        # type: (List[callable], float, str, bool) -> None
        super(Sequence, self).__init__(*a, **k)
        self._steps = deque()  # type: [SequenceStep]
        self._current_step = None  # type: SequenceStep
        self.interval = interval
        self._state = UN_STARTED
        self._res = None
        self._sync = sync
        self._is_inner_seq = False
        self._by_passed = False
        self._start_at = None  # type: float
        self._end_at = None  # type: float
        self._duration = None  # type: float
        # self._debug = debug
        self._debug = debug and not sync
        if not name:
            frame_info = get_frame_info(2)
            if frame_info:
                name = "%s.%s" % (frame_info.class_name, frame_info.method_name)
        self.name = name
        if len(steps):
            self.add(steps, interval=interval)

    def __repr__(self):
        return "seq (%s)" % self.name

    def __len__(self):
        return len(self._steps)

    @property
    def steps(self):
        return list(self._steps)

    def _make_step(self, callback, interval=None, name=None, complete_on=None, by_pass=False):
        return SequenceStep(callback, sequence=self, interval=interval, name=name,
                            complete_on=complete_on, by_pass=by_pass)

    def has_started_check(self):
        if self._state == UN_STARTED and not self._is_inner_seq:
            raise RuntimeError("%s has not been called, check sync parameter" % self)

    def __call__(self):
        if self._state == UN_STARTED:
            self._start_at = time.time()
            self._state = STARTED
            self._exec_next()

    def _exec_next(self):
        if self._state == TERMINATED:
            return
        if self._current_step and self._current_step._res and self._current_step._by_pass:
            self._by_passed = True
            self._sync = False  # prevents sync sequences that use by pass to continue on add
            self._terminate_seq()
            return
        if len(self._steps):
            if self._debug:
                self.parent.log_debug("%s : exec %s" % (self, self._steps[0]),
                                      debug=False)
            self._current_step = self._steps.popleft()
            self._current_step()
        else:
            self._terminate_seq()

    def _terminate_seq(self):
        if self._state == TERMINATED:
            return
        self._state = TERMINATED
        self._end_at = time.time()
        self._duration = self._end_at - self._start_at

        # is None on a sync instantiation
        if self._current_step:
            self._res = self._current_step._res
        if self._debug:
            message = "%s terminated in %.3fs" % (self, self._duration)
            if self._res:
                message += " (res %s)" % self._res
            if self._by_passed:
                message += " - by_passed"
            self.parent.log_debug(message, debug=False)
        # noinspection PyUnresolvedReferences
        self.notify_terminated()

    def add(self, callback=nop, interval=None, name=None, complete_on=None, by_pass=False):
        # type: (Any, float, callable, callable, bool) -> Sequence
        """
            callback can be :
            - None: can be used to just wait on a condition
            - a Sequence : it is wrapped in a SequenceStep and notifies on terminationg
            - a SequenceStep
            - a callable or a list of callable which are added as SequenceStep
        """
        if callback is None:
            return self

        if len(self._steps) == 0 and self._sync is False:
            self.parent.defer(self.has_started_check)

        if callback == nop:
            interval = interval or 0
            name = "wait %s" % interval if interval else "pass"

        if isinstance(callback, Sequence):
            if callback._state == TERMINATED or len(callback) == 0:
                self.parent.log_debug("%s by_passed (no steps)" % callback, debug=False)
                return self
            callback._is_inner_seq = True
            self._steps.append(
                self._make_step(callback, interval=interval, name=name, complete_on=complete_on, by_pass=by_pass))
        elif isinstance(callback, SequenceStep):
            if callback._state == TERMINATED:
                return self
            self._steps.append(callback)
        else:
            callback = [callback] if not isinstance(callback, Iterable) else callback
            [self._steps.append(
                self._make_step(step, interval=interval, name=name, complete_on=complete_on, by_pass=by_pass))
                for step in callback]

        # allows restarting sequence on add()
        if self._state == TERMINATED:
            self._state = UN_STARTED
            self()
        # allows sync execution
        elif self._state == UN_STARTED and self._sync:
            self()

        return self
