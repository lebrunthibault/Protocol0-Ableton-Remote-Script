from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.decorators import timeout_limit
from a_protocol_0.utils.utils import _has_callback_queue, is_lambda, get_callable_name

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.utils.Sequence import Sequence

UN_STARTED = 0
STARTED = 1
TERMINATED = 2


class SequenceStep(AbstractControlSurfaceComponent):
    def __init__(self, func, sequence, interval=None, name=None, complete_on=None, by_pass=False, *a, **k):
        # type: (callable, Sequence, float, str, callable, bool) -> None
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__(*a, **k)
        self._seq = sequence
        self._debug = sequence._debug
        if not callable(func):
            raise RuntimeError("You passed a non callable to a sequence : %s to %s" % (func, self))
        self._callable = func
        self.name = name or get_callable_name(func)
        self._interval = interval if interval is not None else sequence.interval
        # self._interval = 4  # debug
        self._state = UN_STARTED
        self._complete_on = complete_on
        self._check_timeout = 5  # around 3.1 s
        self._check_count = 0
        self._res = None
        self._by_pass = by_pass

    def __repr__(self):
        output = self.name
        if self._interval:
            output += " (and wait %s)" % self._interval
        if self._complete_on:
            if _has_callback_queue(self._complete_on):
                output += " (and wait for listener call : %s)" % get_callable_name(self._complete_on)
            elif is_lambda(self._complete_on):
                output += " (and poll for lambda condition)"
            else:
                output += " (and poll for %s)" % get_callable_name(self._complete_on)
        if self._by_pass:
            output += " (has by_pass)"

        return output

    def __call__(self):
        if self._state != UN_STARTED:
            return

        self._state = STARTED
        self._execute()

    def _check_for_step_completion(self):
        if not self._complete_on:
            if self._interval:
                self.parent._wait(self._interval, self._terminate)
            else:
                self._terminate()
            return

        if self._check_count == self._check_timeout:
            self._step_timed_out()
            return

        elif _has_callback_queue(self._complete_on):
            # listener activation
            # if self._debug:
            #     self.parent.log_debug("%s - step %s : listener activated" % (self._seq, self),
            #                           debug=False)
            # noinspection PyUnresolvedReferences
            self._complete_on._callbacks.append(
                timeout_limit(self._terminate, timeout_limit=pow(2, self._check_timeout),
                              on_timeout=self._step_timed_out))
            return
        elif not self._complete_on():
            # polling
            # if self._debug:
            #     self.parent.log_debug("%s - step %s : polling activated" % (self._seq, self),
            #                           debug=False)

            self.parent._wait(pow(2, self._check_count), self._check_for_step_completion)
            self._check_count += 1
            return

        self._terminate()

    def _handle_sequence_step(self, seq, call=False):
        # type: (Sequence) -> None
        if call:
            seq()
        if seq._state == TERMINATED:
            self._res = seq._res
            self._check_for_step_completion()
        else:
            self._sequence_terminated_listener.subject = seq
        return

    def _execute(self):
        res = self._callable()
        from a_protocol_0.utils.Sequence import Sequence
        if isinstance(self._callable, Sequence):
            return self._handle_sequence_step(seq=self._callable)

        if isinstance(res, Sequence):
            if not is_lambda(self._callable):
                # this must be an error
                raise RuntimeError("Wrong usage of sequence, sequence should be generated synchronously (%s) on %s" % (
                    self, self._seq))
            else:
                return self._handle_sequence_step(seq=res, call=True)

        self._res = res

        if self._res and self._by_pass:
            self._terminate()
        else:
            self._check_for_step_completion()

    def _step_timed_out(self):
        self.parent.log_error("timeout error on sequence step waiting for completion %s" % self._complete_on,
                              debug=False)
        self._res = False
        self._terminate()

    @subject_slot("terminated")
    def _sequence_terminated_listener(self):
        self._res = self._sequence_terminated_listener.subject._res
        self._check_for_step_completion()

    def _terminate(self):
        self._state == TERMINATED
        self._seq._exec_next()
