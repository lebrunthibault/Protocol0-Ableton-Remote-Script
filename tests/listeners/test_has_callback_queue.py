from __future__ import print_function

from typing import List, Any

from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.tests.test_all import p0
from protocol0.domain.shared.decorators import has_callback_queue, p0_subject_slot
Scheduler.defer = classmethod(lambda cls, callback: callback())


def test_has_callback_queue_1():
    # type: () -> None
    res = []

    # noinspection PyClassHasNoInit
    class Example:
        @has_callback_queue()
        def example(self):
            # type: () -> None
            res.append(0)

    obj = Example()
    obj.example.add_callback(lambda: res.append(1))
    obj.example.add_callback(lambda: res.append(2))
    obj.example.add_callback(lambda: res.append(3))

    obj.example()
    assert res == [0, 1, 2, 3]


def test_has_callback_queue_2():
    # type: () -> None
    res = []

    # noinspection PyClassHasNoInit
    class Child:
        @has_callback_queue()
        def example(self):
            # type: () -> None
            res.append("child")

    obj = Child()
    obj.example.add_callback(lambda: res.append("1"))
    obj.example.add_callback(lambda: res.append("2"))
    obj.example.add_callback(lambda: res.append("3"))

    obj.example()
    assert res == ["child", "1", "2", "3"]


def test_has_callback_queue_result():
    # type: () -> None
    class Example(AbstractObject):
        __subject_events__ = ("test",)

        def __init__(self):
            # type: () -> None
            super(Example, self).__init__()
            self.listener_normal.subject = self
            self.listener_sequence.subject = self
            self.callback_called = False

        def test(self):
            # type: () -> None
            from protocol0 import Protocol0
            # noinspection PyUnresolvedReferences
            Protocol0.SELF.defer(self.notify_test)

        @p0_subject_slot("test")
        def listener_normal(self):
            # type: () -> None
            pass

        @p0_subject_slot("test")
        def listener_sequence(self):
            # type: () -> Sequence
            return Sequence().done()

    # 'normal' listener
    obj = Example()
    seq = Sequence()
    seq.add(obj.test, complete_on=obj.listener_normal)
    seq.add(lambda: setattr(obj, "callback_called", True))

    def check_called():
        # type: () -> None
        assert obj.callback_called

    seq.add(check_called)
    seq.done()

    # listener returning sequence
    seq = Sequence()
    seq.add(obj.test, complete_on=obj.listener_sequence)
    seq.add(lambda: setattr(obj, "callback_called", True))
    seq.add(check_called)
    seq.done()


def test_async_callback():
    # type: () -> None
    class Example(AbstractObject):
        __subject_events__ = ("test",)

        def __init__(self, val, test_res, *a, **k):
            # type: (int, List[int], Any, Any) -> None
            super(Example, self).__init__(*a, **k)
            self.val = val
            self.test_res = test_res

        @has_callback_queue()
        def callback_listener(self):
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
        assert test_res_callbacks == [0, 1, 2, 3]

    seq = Sequence()
    seq.add(obj1.callback_listener)  # type: ignore[arg-type]
    seq.add(obj2.callback_listener)  # type: ignore[arg-type]
    seq.add(check_res)
    seq.done()


def test_p0_subject_slot_sequence():
    # type: () -> None
    class Example(AbstractObject):
        __subject_events__ = ("test",)

        def __init__(self, val, test_res, *a, **k):
            # type: (int, List[int], Any, Any) -> None
            super(Example, self).__init__(*a, **k)
            self.val = val
            self.test_res = test_res
            self.subject_slot_listener.subject = self

        @p0_subject_slot("test")
        def subject_slot_listener(self):
            # type: () -> None
            return None

    test_res_callbacks = []  # type: List[int]
    example = Example(0, test_res_callbacks)
    seq = Sequence()
    seq.add(complete_on=example.subject_slot_listener)
    seq.add(lambda: test_res_callbacks.append(1))
    seq.done()
    example.subject_slot_listener()

    def check_res():
        # type: () -> None
        assert test_res_callbacks == [1]

    p0.wait(3, check_res)
