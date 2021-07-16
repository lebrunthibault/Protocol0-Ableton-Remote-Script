from __future__ import print_function

from _Framework.SubjectSlot import Subject, SlotManager, subject_slot

# noinspection PyUnresolvedReferences
from protocol0.tests.test_all import p0


def test_subject_slot_inheritance():
    # type: () -> None
    res = []

    class Emitter(Subject):
        __subject_events__ = ("test",)

        def emit(self):
            # type: () -> None
            # noinspection PyUnresolvedReferences
            self.notify_test()

    class Parent(SlotManager):
        def __init__(self, emitter):
            # type: (Emitter) -> None
            super(Parent, self).__init__()
            self.listener.subject = emitter

        @subject_slot("test")
        def listener(self):
            # type: () -> None
            res.append(1)

    class Child(Parent):
        def __init__(self, emitter):
            # type: (Emitter) -> None
            super(Child, self).__init__(emitter=emitter)
            self.listener.subject = emitter

        @subject_slot("test")
        def listener(self):
            # type: () -> None
            res.append(2)

    emitter = Emitter()
    obj = Parent(emitter)
    emitter.emit()

    assert res == [1]

    obj.listener.subject = None
    obj = Child(emitter)
    emitter.emit()
    assert res == [1, 2]
