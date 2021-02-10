import time
from collections import deque, Iterable
from functools import partial

from typing import List

from a_protocol_0.errors.SequenceError import SequenceError
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.SequenceState import SequenceState, SequenceLogLevel
from a_protocol_0.sequence.SequenceStep import SequenceStep
from a_protocol_0.utils.decorators import subject_slot
from a_protocol_0.utils.utils import get_frame_info, nop


class Sequence(AbstractObject):
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

    DISABLE_LOGGING = False

    def __init__(self, wait=0, log_level=SequenceLogLevel.debug, debug=True, name=None, bypass_errors=False, *a, **k):
        super(Sequence, self).__init__(*a, **k)
        self._steps = deque()  # type: [SequenceStep]
        self._current_step = None  # type: SequenceStep
        self._wait = wait
        self._state = SequenceState.UN_STARTED
        self._res = None
        self._start_at = None  # type: float
        self._end_at = None  # type: float
        self._duration = None  # type: float
        self._log_level = SequenceLogLevel.disabled if self.DISABLE_LOGGING else log_level
        self._debug = (log_level == SequenceLogLevel.debug) and debug and not self.DISABLE_LOGGING
        self._early_returned = False
        self._errored = False
        self._bypass_errors = bypass_errors
        self._parent_seq = None  # type: Sequence
        # self._debug = debug and not sync
        self._is_condition_seq = False
        if not name:
            frame_info = get_frame_info(2)
            if frame_info:
                name = "%s.%s" % (frame_info.class_name, frame_info.method_name)
        self.name = name
        self._done_called = False
        self.terminated_callback = None  # type: callable

        # expecting the method to execute in less than one tick time
        self.parent.defer(self._done_called_check)

    def __repr__(self):
        return "[seq %s]" % self.name

    def __len__(self):
        return len(self._steps)

    @property
    def _parent_seqs(self):
        # type: () -> List[Sequence]
        return [self._parent_seq] + self._parent_seq._parent_seqs if self._parent_seq is not None else []

    def _add_step(self, callback, *a, **k):
        if isinstance(callback, Iterable):
            def parallel_sequence_creator(callbacks):
                from a_protocol_0.sequence.ParallelSequence import ParallelSequence
                seq = ParallelSequence(log_level=self._log_level, debug=self._debug)
                [seq.add(func) for func in callbacks]
                return seq.done()
            callback = partial(parallel_sequence_creator, callback)

        self._steps.append(SequenceStep(callback, sequence=self, log_level=self._log_level, *a, **k))

    def _done_called_check(self):
        if not self._done_called:
            self.parent.log_debug(self._parent_seqs)
        if not self._done_called and not self._early_returned and all(
                [not seq._errored for seq in [self] + self._parent_seqs]):
            raise SequenceError(object=self, message="Sequence.done() has not been called")

    def _start(self):
        if self._state == SequenceState.TERMINATED:
            raise SequenceError(object=self, message="You tried to execute a terminated sequence")
        if self._state == SequenceState.STARTED:
            return
        if self._state == SequenceState.UN_STARTED:
            self._start_at = time.time()

        self._state = SequenceState.STARTED
        self._exec_next()

    def _exec_next(self):
        if self._state == SequenceState.TERMINATED:
            raise SequenceError(object=self, message="You called _exec_next on a terminated sequence")

        if len(self._steps):
            if self._debug:
                self.parent.log_info("%s : exec %s" % (self, self._steps[0]),
                                     debug=False)
            self._current_step = self._steps.popleft()
            self._step_termination.subject = self._current_step
            self._current_step._start()
        elif self._current_step._is_terminal_step:
            self._terminate()
        else:
            self._state = SequenceState.PAUSED

    @subject_slot("terminated")
    def _step_termination(self):
        if (self._current_step._errored or self.song.errored) and not self._bypass_errors:
            self._errored = True
            self._terminate()
        elif self._current_step._early_returned:
            self._early_returned = True
            self._terminate()
        else:
            self._exec_next()

    def _terminate(self):
        if self._state == SequenceState.TERMINATED:
            raise SequenceError(object=self,
                                message="You called _terminate twice")

        if self._current_step and not self._current_step._is_terminal_step and not self._early_returned and not self._errored:
            raise SequenceError(object=self,
                                message="You called _terminate but the last step is not the terminal one")

        self._state = SequenceState.TERMINATED

        if callable(self.terminated_callback) and not self._errored:
            self.terminated_callback()

        self._end_at = time.time()
        self._duration = self._end_at - (self._start_at or self._end_at)
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
            return_if_not=None, check_timeout=5, silent=False):
        """
            callback can be :
            - None: can be used to just wait on a condition
            - a SequenceStep
            - a callable or a list of callable which are added as SequenceStep
        """
        if callback is None:
            return self

        if self._state == SequenceState.TERMINATED:
            if self._early_returned or self._errored:
                return
            raise SequenceError(object=self, message="You called add() but the sequence is terminated")

        if callback == nop:
            name = "wait %s" % wait if wait else "pass"

        if isinstance(callback, Sequence):
            callback._errored = True
            raise SequenceError(object=self,
                                message="You passed a Sequence object instead of a Sequence factory to add")
        else:
            self._add_step(callback, wait=wait, name=name, complete_on=complete_on, do_if=do_if, do_if_not=do_if_not,
                           return_if=return_if, return_if_not=return_if_not, check_timeout=check_timeout, silent=silent)

        if not self._early_returned and self._state in (SequenceState.UN_STARTED, SequenceState.PAUSED):
            # this is the only way to ensure the sequence steps are going to be executed in a sync sequence with sync sequence steps
            self._start()

        return self

    def done(self):
        if self._done_called:
            raise SequenceError(object=self, message="You called done multiple times")
        self._done_called = True

        # e.g. : a totally sync sequence is over (last step is already executed)
        if len(self._steps) == 0:
            if self._current_step:
                self._current_step._is_terminal_step = True
            if self._state in (SequenceState.UN_STARTED, SequenceState.PAUSED):
                self._terminate()
        else:
            self._steps[-1]._is_terminal_step = True

        return self
