from __future__ import print_function

from functools import partial

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.sequence.SequenceState import SequenceLogLevel
from a_protocol_0.utils.decorators import has_callback_queue, subject_slot


def test_async_callback():
    class Example(AbstractObject):
        __subject_events__ = ('test',)

        def __init__(self, val, test_res, *a, **k):
            super(Example, self).__init__(*a, **k)
            self.val = val
            self.test_res = test_res
            self.subject_slot_listener.subject = self

        @has_callback_queue
        def callback_listener(self):
            seq = Sequence(log_level=SequenceLogLevel.disabled)

            self.test_res.append(self.val)
            seq.add(wait=1)
            self.test_res.append(self.val + 1)

            return seq.done()

        @subject_slot("test")
        def subject_slot_listener(self):
            seq = Sequence(log_level=SequenceLogLevel.disabled)

            self.test_res.append(self.val)
            seq.add(wait=1)
            self.test_res.append(self.val + 1)

            return seq.done()

    test_res_callbacks = []
    obj1 = Example(0, test_res_callbacks)
    obj2 = Example(2, test_res_callbacks)

    def check_res(test_res):
        assert test_res_callbacks == [0, 1, 2, 3]

    seq = Sequence(log_level=SequenceLogLevel.disabled)
    seq.add(obj1.callback_listener)
    seq.add(obj2.callback_listener)
    seq.add(partial(check_res, test_res_callbacks))
    seq.done()
