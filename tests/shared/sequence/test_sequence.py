from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def test_sanity_checks():
    # type: () -> None
    seq = Sequence()
    seq.add([])
    seq.done()
    assert seq.state.terminated


def test_async():
    # type: () -> None
    test_res = []
    seq = Sequence()
    seq.defer()
    seq.add(lambda: test_res.append(4), name="add 4")
    seq.done()

    assert test_res == []


def test_wait_for_event():
    test_res = []

    seq = Sequence()
    seq.wait_for_event(BarEndingEvent)
    seq.add(lambda: test_res.append(False), name="appending res seq 1")
    seq.done()

    assert test_res == []
    seq._cancel()

    seq2 = Sequence()
    seq2.wait_for_event(BarEndingEvent)
    seq2.add(lambda: test_res.append(True), name="appending res seq 2")
    seq2.done()

    DomainEventBus.emit(BarEndingEvent())

    assert test_res == [True]


def test_wait_for_event_match():
    test_res = []

    class TestEvent(object):
        def __init__(self, value):
            # type: (int) -> None
            self.value = value

        def target(self):
            # type: () -> int
            return self.value

    seq = Sequence()
    seq.wait_for_event(TestEvent, 2)
    seq.add(lambda: test_res.append(True), name="appending res seq 2")
    seq.done()

    DomainEventBus.emit(TestEvent(1))

    assert test_res == []
    DomainEventBus.emit(TestEvent(2))
    assert test_res == [True]
    seq._cancel()


def test_prompt():
    make_protocol0()

    # noinspection PyShadowingNames
    def create_seq():
        seq = Sequence()
        seq.prompt("question ?")
        seq.add(lambda: test_res.append(True))
        return seq.done()

    test_res = []
    seq = create_seq()
    assert seq.state.started
    assert test_res == []
    seq._cancel()

    test_res = []
    seq = create_seq()
    CommandBus.dispatch(EmitBackendEventCommand("option_selected", data="Yes"))
    assert test_res == [True]
    seq._cancel()

    test_res = []
    seq = create_seq()
    CommandBus.dispatch(EmitBackendEventCommand("option_selected", data="No"))
    assert seq.state.cancelled
    assert test_res == []

    assert test_res == []


def test_select():
    make_protocol0()

    # noinspection PyShadowingNames
    def create_seq():
        seq = Sequence()
        seq.select("question ?", [1, 2, 3])
        seq.add(lambda: test_res.append(seq.res))
        return seq.done()

    test_res = []
    seq = create_seq()
    assert seq.state.started
    assert test_res == []
    seq._cancel()

    test_res = []
    seq = create_seq()
    CommandBus.dispatch(EmitBackendEventCommand("option_selected", 2))
    assert test_res == [2]
    seq._cancel()


def test_cancel():
    test_res = []
    seq = Sequence()
    seq.add(seq._cancel)
    seq.add(lambda: test_res.append(True))
    seq.done()

    assert test_res == []
