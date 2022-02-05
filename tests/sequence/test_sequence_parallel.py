from __future__ import print_function

from typing import List, Any

from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.tests.test_all import p0
from protocol0.domain.shared.decorators import has_callback_queue, p0_subject_slot


def test_parallel_listeners():
    # type: () -> None
    class Example(AbstractObject):
        __subject_events__ = ("test",)

        def __init__(self, val, test_res, *a, **k):
            # type: (int, List[int], Any, Any) -> None
            super(Example, self).__init__(*a, **k)
            self.val = val
            self.test_res = test_res
            self.subject_slot_listener.subject = self

        def test(self):
            # type: () -> None
            # noinspection PyUnresolvedReferences
            self.notify_test()

        @has_callback_queue()
        def callback_listener(self):
            # type: () -> Sequence
            # noinspection PyShadowingNames
            seq = Sequence()

            self.test_res.append(self.val)
            seq.add(wait=1)
            seq.add(lambda: self.test_res.append(self.val + 1))

            return seq.done()

        @p0_subject_slot("test")
        def subject_slot_listener(self):
            # type: () -> Sequence
            # noinspection PyShadowingNames
            seq = Sequence()

            self.test_res.append(self.val)
            seq.add(wait=1)
            seq.add(lambda: self.test_res.append(self.val + 1))

            return seq.done()

    test_res_callbacks = []  # type: List[int]
    obj1 = Example(0, test_res_callbacks)
    obj2 = Example(2, test_res_callbacks)

    def check_res():
        # type: () -> None
        assert test_res_callbacks == [0, 2, 1, 3]

    seq = Sequence()
    seq.add([obj1.callback_listener, obj2.callback_listener])
    seq.add(check_res)
    seq.done()

    # subject_slot

    test_res_subject_slot = []  # type: List[int]
    obj1 = Example(0, test_res_subject_slot)
    obj2 = Example(2, test_res_subject_slot)

    def check_res_2():
        # type: () -> None
        assert test_res_subject_slot == [0, 2, 1, 3] or test_res_subject_slot == [0, 2, 3, 1]

    seq = Sequence()
    p0.defer(obj1.test)
    p0.defer(obj2.test)
    seq.add([obj1.subject_slot_listener.listener, obj2.subject_slot_listener.listener])
    seq.add(check_res_2)
    seq.done()
