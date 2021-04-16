from __future__ import print_function

from _Framework.SubjectSlot import Subject, SlotManager, subject_slot

# noinspection PyUnresolvedReferences
from a_protocol_0.tests.test_all import p0


def test_subject_slot_inheritance():
    res = []

    class Emitter(Subject):
        __subject_events__ = ("test",)

        def emit(self):
            # noinspection PyUnresolvedReferences
            self.notify_test()

    class Parent(SlotManager):
        def __init__(self, emitter):
            super(Parent, self).__init__()
            self.listener.subject = emitter

        @subject_slot("test")
        def listener(self):
            res.append(1)

    class Child(Parent):
        def __init__(self, emitter):
            super(Child, self).__init__(emitter=emitter)
            self.listener.subject = emitter

        @subject_slot("test")
        def listener(self):
            res.append(2)

    emitter = Emitter()
    obj = Parent(emitter)
    emitter.emit()

    assert res == [1]

    obj.listener.subject = None
    obj = Child(emitter)
    emitter.emit()
    assert res == [1, 2]
