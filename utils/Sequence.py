from collections import deque, Iterable
from typing import List, Any

from a_protocol_0.utils.log import log_ableton


class SequenceStep(object):
    def __init__(self, func, sequence, interval=1, do_while=False, *a, **k):
        # type: (callable, Sequence, float, bool) -> None
        super(SequenceStep, self).__init__(*a, **k)
        self._seq = sequence
        self._callable = func
        self._interval = interval if interval is not None else sequence._interval
        self._do_while = do_while
        self._timeout = 4
        self._count = 0

    def __repr__(self):
        return "%s (%s)" % (self._callable, self._interval)

    def __call__(self):

        def execute_callback():
            if self._count == self._timeout:
                log_ableton("timeout error on sequence step waiting for do_while %s" % self._do_while)
                return
            self._callable()

            if self._do_while and self._do_while():
                Protocol0.SELF._wait(pow(2, self._count), execute_callback)
            self._seq.notify_step_done()
            self._count += 1

        from a_protocol_0 import Protocol0
        Protocol0.SELF._wait(self._interval, execute_callback)


class Sequence(object):
    """ run a simple sequence of asynchronous actions """

    def __init__(self, steps=[], interval=1, offset=0, on_finish=[], timeout=None, name="anon seq", outer_seq=None, debug=False, *a, **k):
        # type: (List[callable], float, float, Any, float, str, Sequence) -> None
        super(Sequence, self).__init__(*a, **k)
        self._steps = deque()  # type: [SequenceStep]
        self._interval = interval
        self._is_running = False
        self._is_completed = False
        self._name = name
        self._outer_seq = outer_seq  # type: Sequence
        self._debug = debug

        if offset:
            self.add(lambda: None, interval=offset)
        self.add(steps)
        if on_finish:
            if isinstance(on_finish, Sequence):
                self._on_finish = on_finish
            elif callable(on_finish):
                self._on_finish = Sequence(on_finish, interval=0)
        else:
            self._on_finish = None

        if timeout:
            from a_protocol_0 import Protocol0
            Protocol0.SELF._wait(timeout, self._execute_on_finish)

    def __repr__(self):
        return "seq %s (%s) : %s" % (self._name, self._interval, list(self._steps))

    def __call__(self):
        if not self._is_running and not self._is_completed:
            self._is_running = True
            self._exec_next()

    @property
    def steps(self):
        return list(self._steps)

    def notify_step_done(self):
        self._exec_next()

    def add_on_finish(self, callback, interval=None):
        self._on_finish = self._on_finish or Sequence()
        self._on_finish.add(callback, interval=interval)

    def add(self, callback, interval=None, do_while=None):
        # type: (callable, float, callable) -> Sequence
        if isinstance(callback, Sequence):
            if do_while:
                raise "do_while is not available for Sequence"
            callback._outer_seq = self
            self._steps.append(callback)
        else:
            callback = [callback] if not isinstance(callback, Iterable) else callback
            [self._steps.append(SequenceStep(step, sequence=self, interval=interval, do_while=do_while)) for step in callback]

        if self._is_completed:
            self._is_completed = False
            self._is_running = False
            self()

        return self

    def add_finish(self, callback, interval=None, do_while=None):
        # type: (callable, float, callable) -> Sequence
        if isinstance(callback, Sequence):
            if do_while:
                raise "do_while is not available for Sequence"
            callback._outer_seq = self
            self._steps.append(callback)
        else:
            self._steps.append(SequenceStep(callback, sequence=self, interval=interval, do_while=do_while))

        return self

    def _execute_on_finish(self):
        if self._on_finish:
            self._on_finish()
            self._on_finish = None

    def _exec_next(self):
        if self._is_completed:
            return
        if len(self._steps):
            if self._debug:
                log_ableton("%s : %s (%s)" % (self._name, self._steps[0], len(self._steps)))
            self._steps.popleft()()
            return

        if self._debug:
            log_ableton("%s is finished" % self._name)

        self._execute_on_finish()
        if self._outer_seq:
            self._outer_seq.notify_step_done()
        self._is_running = False
        self._is_completed = True
