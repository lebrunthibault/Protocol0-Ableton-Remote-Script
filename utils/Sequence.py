from collections import deque
from typing import List

from a_protocol_0.utils.log import log_ableton


class SequenceStep(object):
    def __init__(self, func, sequence, interval=1, notify=True, do_while=False, *a, **k):
        # type: (callable, Sequence, float, bool) -> None
        super(SequenceStep, self).__init__(*a, **k)
        self._seq = sequence
        self._callable = func
        self._interval = interval if interval is not None else sequence._interval
        self._notify = notify
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
            if self._notify:
                self._seq.notify_step_done()
            self._count += 1

        from a_protocol_0 import Protocol0
        Protocol0.SELF._wait(self._interval, execute_callback)


class Sequence(object):
    """ run a simple sequence of asynchronous actions """

    def __init__(self, steps=[], interval=1, offset=0, on_finish=None, timeout=None, name="anon seq", outer_seq=None, *a, **k):
        # type: (List[callable], float, float, callable, float, str, Sequence) -> None
        super(Sequence, self).__init__(*a, **k)
        self._steps = deque()  # type: [SequenceStep]
        if offset:
            self._steps.append(SequenceStep(lambda: None, sequence=self, interval=offset))
        [self._steps.append(SequenceStep(step, sequence=self, interval=interval)) for step in steps]
        self._interval = interval
        self._on_finish = SequenceStep(on_finish, sequence=self, interval=0, notify=False) if on_finish else None
        self._is_running = False
        self._is_completed = False
        self._name = name
        self._outer_seq = outer_seq  # type: Sequence

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

    def add(self, callback, interval=None, do_while=None):
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
            log_ableton("%s : %s (%s)" % (self._name, self._steps[0], len(self.steps)))
            self._steps.popleft()()
            return

        log_ableton("%s is finished" % self._name)

        self._execute_on_finish()
        if self._outer_seq:
            self._outer_seq.notify_step_done()
        self._is_running = False
        self._is_completed = True
