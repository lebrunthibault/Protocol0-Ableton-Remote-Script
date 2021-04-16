from __future__ import print_function

from functools import partial

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.Sequence import Sequence

# noinspection PyUnresolvedReferences
from a_protocol_0.tests.test_all import p0
from a_protocol_0.utils.decorators import has_callback_queue, p0_subject_slot, defer


def test_has_callback_queue_1():
    res = []

    class Example:
        @has_callback_queue(immediate=True)
        def example(self):
            res.append(0)

    obj = Example()
    obj.example.add_callback(lambda: res.append(1))
    obj.example.add_callback(lambda: res.append(2))
    obj.example.add_callback(lambda: res.append(3))

    obj.example()
    assert res == [0, 1, 2, 3]


def test_has_callback_queue_2():
    res = []

    class Parent:
        @has_callback_queue()
        def example(self):
            res.append("parent")

    class Child:
        @has_callback_queue(immediate=True)
        def example(self):
            res.append("child")

    obj = Child()
    obj.example.add_callback(lambda: res.append(1))
    obj.example.add_callback(lambda: res.append(2))
    obj.example.add_callback(lambda: res.append(3))

    obj.example()
    assert res == ["child", 1, 2, 3]


def test_has_callback_queue_result():
    test_res = []

    class Example(AbstractObject):
        __subject_events__ = ("test",)

        def __init__(self):
            super(Example, self).__init__()
            self.listener_normal.subject = self
            self.listener_sequence.subject = self
            self.callback_called = False

        @defer
        def test(self):
            # noinspection PyUnresolvedReferences
            self.notify_test()

        @p0_subject_slot("test", immediate=False)
        def listener_normal(self):
            pass

        @p0_subject_slot("test", immediate=True)
        def listener_sequence(self):
            return Sequence().done()

    test_res = {"callback_called": False}

    # 'normal' listener
    obj = Example()
    seq = Sequence()
    seq.add(obj.test, complete_on=obj.listener_normal)
    seq.add(lambda: setattr(obj, "callback_called", True))

    def check_called():
        assert obj.callback_called

    seq.add(check_called)
    seq.done()

    # listener returning sequence
    test_res = {"callback_called": False}
    seq = Sequence()
    seq.add(obj.test, complete_on=obj.listener_sequence)
    seq.add(lambda: setattr(obj, "callback_called", True))

    def check_called():
        assert obj.callback_called

    seq.add(check_called)
    seq.done()


def test_async_callback():
    class Example(AbstractObject):
        __subject_events__ = ("test",)

        def __init__(self, val, test_res, *a, **k):
            super(Example, self).__init__(*a, **k)
            self.val = val
            self.test_res = test_res
            self.subject_slot_listener.subject = self

        @has_callback_queue()
        def callback_listener(self):
            seq = Sequence(silent=True)

            self.test_res.append(self.val)
            seq.add(wait=1)
            seq.add(lambda: self.test_res.append(self.val + 1))

            return seq.done()

        @p0_subject_slot("test")
        def subject_slot_listener(self):
            seq = Sequence(silent=True)

            self.test_res.append(self.val)
            seq.add(wait=1)
            seq.add(lambda: self.test_res.append(self.val + 1))

            return seq.done()

    test_res_callbacks = []
    obj1 = Example(0, test_res_callbacks)
    obj2 = Example(2, test_res_callbacks)

    def check_res(test_res):
        assert test_res_callbacks == [0, 1, 2, 3]

    seq = Sequence(silent=True)
    seq.add(obj1.callback_listener)
    seq.add(obj2.callback_listener)
    seq.add(partial(check_res, test_res_callbacks))
    seq.done()
