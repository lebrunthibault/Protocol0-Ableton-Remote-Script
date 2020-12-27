from collections import deque, Iterable
from typing import List, Any

from a_protocol_0.utils.decorators import timeout_limit
from a_protocol_0.utils.log import log_ableton
from a_protocol_0.utils.utils import get_frame_info, nop


class SequenceStep(object):
    def __init__(self, func, sequence, interval=1, name=None, do_when=None, notify_after=None, *a, **k):
        # type: (callable, Sequence, float, str, callable, callable) -> None
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__(*a, **k)
        self._seq = sequence
        self._debug = sequence._debug
        self._callable = func
        self.name = name or func
        self._interval = interval if interval is not None else sequence.interval
        if isinstance(func, Sequence):
            self._interval = 0
        self._do_when = do_when
        self._notify_after = notify_after
        self._check_timeout = 5  # around 3.1 s
        self._count = 0

    def __repr__(self):
        output = "%s (%s)" % (self.name, self._interval)
        if self._do_when:
            output += " (has_do_when)"
        if self._notify_after:
            output += " (has_notify_after)"

        return output

    def _has_callback_queue(self, func):
        return hasattr(func, "_has_callback_queue") and hasattr(func, "_callbacks")

    def __call__(self):
        def execute_check(check, success_callback):
            if not check:
                success_callback()
                return

            if self._count == self._check_timeout:
                log_ableton("timeout error on sequence step waiting for check %s" % self._do_when, debug=False)
                return

            if self._has_callback_queue(check):
                # listener activation
                if self._debug:
                    log_ableton("%s - step %s : listener activated -> %s" % (self._seq, self, check), debug=False)
                check._callbacks.append(timeout_limit(success_callback, pow(2, self._check_timeout)))
                return
            elif not check():
                # polling
                if self._debug:
                    log_ableton("%s - step %s : polling activated -> %s" % (self._seq, self, check), debug=False)
                Protocol0.SELF._wait(pow(2, self._count), execute_step)
                self._count += 1
                return

            success_callback()

        def execute_step():
            self._callable()
            execute_check(self._notify_after, self._seq._exec_next)

        from a_protocol_0 import Protocol0
        Protocol0.SELF._wait(self._interval, lambda: execute_check(self._do_when, execute_step))


class Sequence(object):
    """
        replacement of the _Framework Task as it does not seem to allow conditional steps like triggers from listeners
        and also I didn't check it before doing that.
        Defines 2 separate slots of execution (which are both a Sequence object) :
            - The main loop
            - The finish loop
        Slot order of execute will always be respected unless the main loop is restarted by calling add()
        Sequence notify their wrapping sequence if it exists allowing sequence nesting
        This condition can be either
            - a callable : in this case an exponential polling is setup
            - a CallbackDescriptor : the step executes when the callback added to the CallbackDescriptor is executed
                This allows for listener reactive chaining
        The condition supports 2 check callbacks :
            _ do_when : wait for a condition to be True before executing
            _ notify_after : wait for a condition to be True before continuing sequence
    """
    UN_STARTED = 0
    STARTED = 1
    TERMINATION_SCHEDULED = 2
    TERMINATED = 3

    def __init__(self, steps=[], interval=0, debug=True, name=None):
        # type: (List[callable], float) -> None
        self._steps = deque()  # type: [SequenceStep]
        self.interval = interval
        self._state = Sequence.UN_STARTED
        if not name:
            func_info = get_frame_info(2)
            if func_info:
                (filename, line, method) = func_info
                name = method
        self.name = name
        self._outer_seq = None  # type: Sequence
        self._debug = debug
        self.add(steps, interval=interval)
        self._on_finish = None  # type: Sequence

    def __repr__(self):
        return "seq (%s)" % self.name

    @property
    def steps(self):
        return list(self._steps)

    @property
    def is_pending_termination(self):
        return self._state in [Sequence.TERMINATION_SCHEDULED, Sequence.TERMINATED]

    def _make_step(self, callback, interval=None, name=None, do_when=None, notify_after=None):
        return SequenceStep(callback, sequence=self, interval=interval, name=name, do_when=do_when, notify_after=notify_after)

    def __call__(self, terminating_callback=None):
        if self._state == Sequence.UN_STARTED:
            self._state = Sequence.STARTED
            if terminating_callback:
                if self._on_finish:
                    self.add_on_finish(terminating_callback, interval=0)
                else:
                    self.add(terminating_callback, interval=0)
            self._exec_next()

    def _exec_next(self):
        if self.is_pending_termination:
            return
        if len(self._steps):
            if self._debug:
                log_ableton("%s : exec %s (remaining %s)" % (self, self._steps[0], len(self._steps) - 1), debug=False)
            self._steps.popleft()()
            return

        # if self._debug:
        #     log_ableton("%s : main loop terminated" % self, debug=False)

        if self._on_finish:
            self._on_finish(self._terminate_seq)
            self._on_finish = None
            self._state = Sequence.TERMINATION_SCHEDULED
        else:
            self._terminate_seq()

    def _terminate_seq(self):
        if self._state == Sequence.TERMINATED:
            return
        self._state == Sequence.TERMINATED
        if self._outer_seq:
            self._outer_seq._exec_next()
        if self._debug:
            log_ableton("%s is terminated" % self, debug=False)

    def add(self, callback=nop, interval=None, name=None, do_when=None, notify_after=None):
        # type: (Any, float, callable, callable) -> Sequence
        """
            callback can be :
            - None: can be used to just wait on a condition
            - a Sequence : it is wrapped in a SequenceStep and notifies on terminationg
            - a SequenceStep
            - a callable or a list of callable which are added as SequenceStep
        """
        if callback is None:
            return

        if callback == nop:
            interval = 0
            name = "pass"

        if isinstance(callback, Sequence):
            callback._outer_seq = self
            self._steps.append(self._make_step(callback, name=name, do_when=do_when, notify_after=notify_after))
        elif isinstance(callback, SequenceStep):
            self._steps.append(callback)
        else:
            callback = [callback] if not isinstance(callback, Iterable) else callback
            [self._steps.append(self._make_step(step, interval=interval, name=name, do_when=do_when, notify_after=notify_after))
             for step in callback]

        # allows restarting sequence on add()
        if self.is_pending_termination:
            self._state = Sequence.UN_STARTED
            self()

        return self

    def add_on_finish(self, callback, interval=None, name=None):
        self._on_finish = self._on_finish or Sequence(name="%s - on_finish" % self.name)
        self._on_finish.add(callback, interval=interval, name=name)

        return self
