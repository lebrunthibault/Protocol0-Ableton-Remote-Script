from __future__ import print_function

from _Framework.SubjectSlot import Subject, SlotManager
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.tests.test_all import p0
from a_protocol_0.utils.decorators import has_callback_queue, subject_slot


def test_has_callback_queue():
    res = []

    class Example:
        @has_callback_queue
        def example(self):
            res.append(0)

    obj = Example()
    obj.example.add_callback(lambda: res.append(1))
    obj.example.add_callback(lambda: res.append(2))
    obj.example.add_callback(lambda: res.append(3))

    obj.example()
    assert res == [0, 1, 2, 3]


def test_has_callback_queue():
    res = []

    class Parent:
        @has_callback_queue
        def example(self):
            res.append("parent")

    class Child:
        @has_callback_queue
        def example(self):
            res.append("child")

    obj = Child()
    obj.example.add_callback(lambda: res.append(1))
    obj.example.add_callback(lambda: res.append(2))
    obj.example.add_callback(lambda: res.append(3))

    obj.example()
    assert res == ["child", 1, 2, 3]

def test_has_callback_queue_result():
    res = []

    class Emitter(Subject):
        __subject_events__ = ('test',)

        def test(self):
            # noinspection PyUnresolvedReferences
            self.notify_test()

    class Example(SlotManager):
        def __init__(self, emitter):
            super(Example, self).__init__()
            self.example.subject = emitter
            self.callback_called = False

        @subject_slot("test")
        def example(self):
            print("exec example")
            return Sequence(name="example listener").add(lambda: print("after wait")).done()

    with p0.component_guard():
        obj = Example(Emitter())
        print("\n")
        seq = Sequence(name="main")

        res = {"callback_called": False}

        seq.add(lambda: print("before callback"), complete_on=obj.example, name="async step").done()
        seq.add(lambda: setattr(obj, "callback_called", True))
        obj.example.listener()
        assert obj.callback_called
