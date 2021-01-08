import time
from collections import deque, Iterable
from typing import List, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.sequence.SequenceError import SequenceError
from a_protocol_0.sequence.SequenceState import SequenceState, DebugLevel
from a_protocol_0.sequence.SequenceStep import SequenceStep
from a_protocol_0.utils.utils import get_frame_info, nop


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
            - via wait which leverages Live 100ms tick for short and hard to check tasks like click on the interface
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
        Conditional execution of steps is available via do_if and do_if_not which can be any argument to Sequence.add
            - The condition is executed *before* the main callable and can bypass the step depending on the result
        return_if and return_if_not are similar but will end the enclosing sequence early instead.
            These 2 callables are going to be executed *before* the main callable which can therefore not be called
            These should better be execute in a step if only return_if so that it's clearer
    """

    def __init__(self, wait=0, debug=DebugLevel.debug, name=None, auto_start=False, parent_seq=None, *a, **k):
        # type: (List[callable], float, str, bool, bool, Sequence) -> None
        super(Sequence, self).__init__(*a, **k)
        self._steps = deque()  # type: [SequenceStep]
        self._current_step = None  # type: SequenceStep
        self._wait = wait
        self._state = SequenceState.UN_STARTED
        self._res = None
        self._auto_start = auto_start
        self._start_at = None  # type: float
        self._end_at = None  # type: float
        self._duration = None  # type: float
        self._debug = (debug == DebugLevel.dev or auto_start is False)
        self._early_returned = False
        self._errored = False
        self._parent_seq = parent_seq  # type: Sequence
        # self._debug = debug and not sync
        self._is_condition_seq = False
        self._done_called = False
        if not name:
            frame_info = get_frame_info(2)
            if frame_info:
                name = "%s.%s" % (frame_info.class_name, frame_info.method_name)
        self.name = name

        self.parent.defer(self.has_started_check)

    def __repr__(self):
        return "[seq %s]" % self.name

    def __len__(self):
        return len(self._steps)

    @property
    def _parent_seqs(self):
        if self._parent_seq is not None:
            return [self._parent_seq] + self._parent_seq._parent_seqs
        else:
            return []

    def _add_step(self, callback, *a, **k):
        return self._steps.append(SequenceStep(callback, sequence=self, *a, **k))

    def has_started_check(self):
        if self._state != SequenceState.UN_STARTED or self._is_condition_seq or self._parent_seq:
            return
        if not self._errored and all([not seq._errored for seq in self._parent_seqs]):
            raise SequenceError(sequence=self, message="seq has not been called or added to a parent sequence")

    def __call__(self):
        if self._state == SequenceState.UN_STARTED:
            self._start_at = time.time()
            self._state = SequenceState.STARTED
            self._exec_next()
        elif self._auto_start and self._state == SequenceState.PAUSED:
            self._state = SequenceState.STARTED
            self._exec_next()
        else:
            raise SequenceError(sequence=self, message="You called an executing sequence")

    def _exec_next(self):
        if self._state == SequenceState.TERMINATED:
            return

        if len(self._steps):
            if self._debug:
                self.parent.log_info("%s : exec %s" % (self, self._steps[0]),
                                     debug=False)
            self._current_step = self._steps.popleft()
            self._current_step()
        elif not self._current_step or self._current_step._is_terminal_step:
            self._terminate()
        elif self._auto_start:
            self._state = SequenceState.PAUSED
        else:
            raise SequenceError("Unknown state reached in _exec_next")

    def _terminate(self):
        if self._current_step and self._current_step._errored and not self._is_condition_seq:
            self._errored = True

        if self._current_step and not self._current_step._is_terminal_step and not self._early_returned and not self._errored:
            raise SequenceError(sequence=self,
                                message="You called _terminate but the last step is not the terminal one")

        if self._state == SequenceState.TERMINATED:
            raise SequenceError(sequence=self, message="You called _terminate twice on %s" % self)

        self._state = SequenceState.TERMINATED

        self._end_at = time.time()
        self._duration = self._end_at - self._start_at
        self._res = self._current_step._res if self._current_step else None

        if self._debug:
            verb = "errored" if self._errored else "terminated successfully"

            message = "%s %s" % (self, verb)
            if not self._current_step:
                message += " (empty seq)"
            # message = "%s %s in %.3fs" % (self, verb, self._duration)
            if self._res:
                message += " (res %s)" % self._res
            if self._early_returned:
                message += " - early return"

            if self._errored:
                self.parent.log_error(message, debug=False)
            else:
                self.parent.log_info(message, debug=False)
        # noinspection PyUnresolvedReferences
        self.notify_terminated()

    def add(self, callback=nop, wait=None, name=None, complete_on=None, do_if=None, do_if_not=None, return_if=None,
            return_if_not=None):
        # type: (Any, float, str, callable, callable, callable, callable, callable) -> Sequence
        """
            callback can be :
            - None: can be used to just wait on a condition
            - a SequenceStep
            - a callable or a list of callable which are added as SequenceStep
        """
        if callback is None:
            return self

        if not callable(callback):
            raise SequenceError(sequence=self,
                                message="You passed a non callable to a sequence : %s to %s, type: %s" % (
                                    callback, self, type(callback)))

        if callback == nop:
            name = "wait %s" % wait if wait else "pass"

        if isinstance(callback, Sequence):
            callback._errored = True
            raise SequenceError(sequence=self,
                                message="You passed a Sequence object instead of a function returning a Sequence to add")
        elif isinstance(callback, SequenceStep) and callback._state != SequenceState.TERMINATED:
            self._steps.append(callback)
        else:
            callbacks = [callback] if not isinstance(callback, Iterable) else callback
            [self._add_step(func, wait=wait, name=name, complete_on=complete_on, do_if=do_if, do_if_not=do_if_not,
                            return_if=return_if, return_if_not=return_if_not) for func in callbacks]

        if self._auto_start and not self._early_returned and self._state in (SequenceState.UN_STARTED, SequenceState.PAUSED):
            # this is the only way to ensure the sequence steps are going to be executed in a sync sequence with sync sequence steps
            self()

        return self

    def done(self):
        if self._done_called:
            raise SequenceError(sequence=self, message="You cannot call done on a sequence multiple times")

        self._done_called = True
        # e.g. : a totally sync sequence is over (last step is already executed)
        if len(self._steps) == 0:
            if self._current_step:
                self._current_step._is_terminal_step = True
            if self._auto_start:
                self._terminate()
        else:
            self._steps[-1]._is_terminal_step = True

        return self
