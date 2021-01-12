from __future__ import print_function

from _Framework.SubjectSlot import Subject, SlotManager
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.tests.test_all import p0
from a_protocol_0.utils.decorators import has_callback_queue, subject_slot
from a_protocol_0.utils.log import log_ableton


# def test_has_callback_queue():
#     res = []
#
#     class Example:
#         @has_callback_queue
#         def example(self):
#             res.append(0)
#
#     e = Example()
#     e.example._callbacks.append(lambda: res.append(1))
#     e.example._callbacks.append(lambda: res.append(2))
#     e.example._callbacks.append(lambda: res.append(3))
#
#     e.example()
#     assert res == [0, 1, 2, 3]
#
#
# def test_has_callback_queue():
#     res = []
#
#     class Parent:
#         @has_callback_queue
#         def example(self):
#             res.append("parent")
#
#     class Child:
#         @has_callback_queue
#         def example(self):
#             res.append("child")
#
#     obj = Child()
#     obj.example._callbacks.append(lambda: res.append(1))
#     obj.example._callbacks.append(lambda: res.append(2))
#     obj.example._callbacks.append(lambda: res.append(3))
#
#     obj.example()
#     assert res == ["child", 1, 2, 3]

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

        @subject_slot("test")
        def example(self):
            print("exec example")
            return Sequence(name="example listener").add(wait=2).add(lambda: print("after wait")).done()

    with p0.component_guard():
        e = Example(Emitter())
        print("\n")
        seq = Sequence(name="main")
        seq.add(lambda: print("before callback"), complete_on=e.example, check_timeout=1, name="async step").done()
        e.example.listener()
        log_ableton(e.example._callbacks)
