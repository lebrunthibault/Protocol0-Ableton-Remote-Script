from __future__ import print_function

from _Framework.SubjectSlot import Subject, subject_slot, SlotManager


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
        def __init__(self, source_emitter):
            # type: (Emitter) -> None
            super(Parent, self).__init__()
            self.listener.subject = source_emitter

        @subject_slot("test")
        def listener(self):
            # type: () -> None
            res.append(1)

    class Child(Parent):
        def __init__(self, source_emitter):
            # type: (Emitter) -> None
            super(Child, self).__init__(source_emitter=source_emitter)
            self.listener.subject = source_emitter

        @subject_slot("test")
        def listener(self):
            # type: () -> None
            res.append(2)

    emitter = Emitter()
    obj = Parent(emitter)
    emitter.emit()

    assert res == [1]

    obj.listener.subject = None
    _ = Child(emitter)
    emitter.emit()
    assert res == [1, 2]
