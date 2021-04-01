import time
from collections import deque, Iterable
from functools import partial

from typing import List, Deque

from a_protocol_0.errors.SequenceError import SequenceError
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.SequenceState import SequenceState, SequenceLogLevel
from a_protocol_0.sequence.SequenceStep import SequenceStep
from a_protocol_0.utils.decorators import p0_subject_slot
from a_protocol_0.utils.utils import get_frame_info, nop


class Sequence(AbstractObject):
    __subject_events__ = ('terminated',)

    """
        Replacement of the _Framework Task as it does not seem to allow variable timeouts like triggers from listeners.
            Nothing but some pale asyncio imitation. Can't wait for python3
        A Sequence usually represents a number of statements (usually a whole method) and a SequenceStep one statement
        A Sequence step is very often a function call that could return a Sequence.
        That is Sequences can be nested allowing deep asynchronous function calls.
        A Sequence should never be passed to the called code but instead the called code should return it's own sequence to be appended (and executed) to the calling one.
        
        Attention : The called code is gonna be called synchronously, any data lookup (e.g. on Live API)
                is gonna be computed at sequence instantiation time and not at sequence runtime !
                If you don't want this behavior to happen, wrap your lookup calls in a step
                Ideally, an asynchronous method should wrap all it's statements in a sequence and do lookups in lambda functions
        The code can declare asynchronous behavior in 2 ways:
            - via wait which leverages Live 100ms tick for tasks where we have a rough idea of the delay and guess without too much hassle
            - via the on_complete argument that defers the completion of the step until a condition is satisfied
        This condition can be either
            - a simple callable returning a bool : in this case an exponential polling is setup with a timeout
            - a CallbackDescriptor decorated function (a function decorate by @p0_subject_slot) : the step executes when the function is called next.
            This is the best part because it allows us to react to the execution of Live listeners
            or even our own listeners. Thus being a shortcut to define yet another listener on an already listened to subject.
            To be clearer it is equivalent to defining a method listening on a subject (a listener) that would call back the sequence when executed.
        A sequence step should always define it's completion step and not expect the next step to handle any timeout or checks
            Example : A step song.create_midi_track should define it's completion check to be the next call to the _added_track_listener.
            Like this any step can always be assured that it executes after the previous one has succeeded or failed (thus ending the sequence).
        after instantiating a sequence by e.g. seq = Sequence(..) you should always call seq.done() to start the sequence execution.
        If not the sequence is not going to be called and an exception will be thrown at the next tick. 
        Conditional execution of steps is available via do_if and do_if_not which can be any argument to Sequence.add
            - The condition is executed *before* the main callable and can bypass the step depending on the result
        return_if and return_if_not are similar but will end the enclosing sequence early instead.
            These 2 callables are going to be executed *before* the main callable which can therefore not be called
            This is rarely needed but if needed it's better to put return_if or return_if_not in an empty step (without a callable) so that it's clearer
    """

    DISABLE_LOGGING = False

    def __init__(self, wait=0, log_level=SequenceLogLevel.debug, debug=True, name=None, bypass_errors=False, silent=False, *a, **k):
        super(Sequence, self).__init__(*a, **k)
        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: SequenceStep
        self._wait = wait
        self._state = SequenceState.UN_STARTED
        self._res = None
        self._start_at = None  # type: float
        self._end_at = None  # type: float
        self._duration = None  # type: float
        self._log_level = SequenceLogLevel.disabled if self.DISABLE_LOGGING or silent else log_level
        self._debug = (self._log_level == SequenceLogLevel.debug) and debug and not self.DISABLE_LOGGING
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
        if not self._done_called and not self._early_returned and all(
                [not seq._errored for seq in [self] + self._parent_seqs]):
            raise SequenceError(object=self, message="Sequence.done() has not been called for %s" % self)

    def _start(self):
        if self._state == SequenceState.TERMINATED:
            self.parent.log_error("You tried to execute a terminated sequence: %s" % self)
            return
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
            self._current_step = self._steps.popleft()
            if self._debug and not self._current_step._silent:
                self.parent.log_info("%s : %s" % (self, self._current_step),
                                     debug=False)
            self._step_termination.subject = self._current_step
            self._current_step._start()
        elif self._current_step._is_terminal_step:
            self._terminate()
        else:
            self._state = SequenceState.PAUSED

    @p0_subject_slot("terminated")
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
            elif self._debug:
                pass
                # self.parent.log_info(message, debug=False)

        # noinspection PyUnresolvedReferences
        self.notify_terminated()

    def add(self, callback=nop, wait=None, name=None, complete_on=None, do_if=None, do_if_not=None, return_if=None,
            return_if_not=None, check_timeout=7, no_timeout=False, silent=False, log_level=SequenceLogLevel.debug):
        """ check_timeout is in live ticks """
        if no_timeout:
            check_timeout = 0
        """
            callback can be :
            - not given (nop): can be used to just wait on a condition
            - a SequenceStep
            - a callable or a list of callable which are added as SequenceStep
        """
        if callback is None:
            return self

        if self._state == SequenceState.TERMINATED:
            if self._early_returned or self._errored:
                return
            raise SequenceError(object=self, message="You called add() but the sequence is terminated")

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
        # type: () -> Sequence
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
