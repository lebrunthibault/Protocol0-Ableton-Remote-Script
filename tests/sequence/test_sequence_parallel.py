from __future__ import print_function

from functools import partial

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.sequence.SequenceState import SequenceLogLevel
# noinspection PyUnresolvedReferences
from a_protocol_0.tests.test_all import p0
from a_protocol_0.utils.decorators import has_callback_queue, subject_slot


def test_parallel_listeners():
    class Example(AbstractObject):
        __subject_events__ = ('test',)

        def __init__(self, val, test_res, *a, **k):
            super(Example, self).__init__(*a, **k)
            self.val = val
            self.test_res = test_res
            self.subject_slot_listener.subject = self

        def test(self):
            # noinspection PyUnresolvedReferences
            self.notify_test()

        @has_callback_queue
        def callback_listener(self):
            seq = Sequence(log_level=SequenceLogLevel.disabled)

            self.test_res.append(self.val)
            seq.add(wait=3)
            seq.add(lambda: self.test_res.append(self.val + 1))

            return seq.done()

        @subject_slot("test")
        def subject_slot_listener(self):
            seq = Sequence(log_level=SequenceLogLevel.disabled)

            self.test_res.append(self.val)
            seq.add(wait=3)
            seq.add(lambda: self.test_res.append(self.val + 1))

            return seq.done()

    test_res_callbacks = []
    obj1 = Example(0, test_res_callbacks)
    obj2 = Example(2, test_res_callbacks)

    def check_res(test_res):
        assert test_res_callbacks == [0, 2, 1, 3]

    seq = Sequence(log_level=SequenceLogLevel.disabled)
    seq.add([obj1.callback_listener, obj2.callback_listener])
    seq.add(partial(check_res, test_res_callbacks))
    seq.done()

    # subject_slot

    test_res_subject_slot = []
    obj1 = Example(0, test_res_subject_slot)
    obj2 = Example(2, test_res_subject_slot)

    def check_res(test_res):
        assert test_res_subject_slot == [0, 2, 1, 3] or test_res_subject_slot == [0, 2, 3, 1]

    seq = Sequence(log_level=SequenceLogLevel.disabled)
    # p0.defer(obj1.test)
    # p0.defer(obj2.test)
    seq.add([obj1.subject_slot_listener.listener, obj2.subject_slot_listener.listener])
    seq.add(partial(check_res, test_res_subject_slot))
    seq.done()
