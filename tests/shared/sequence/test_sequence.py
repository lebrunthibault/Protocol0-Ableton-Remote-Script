import pytest

from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import has_callback_queue
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.utils import nop
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.tests.fixtures.p0 import make_protocol0


def test_sanity_checks():
    # type: () -> None
    seq = Sequence()
    seq.add([])
    seq.done()
    assert seq.terminated

    with pytest.raises(Protocol0Error):
        Sequence().add(wait=1, complete_on=lambda: True).done()

    with pytest.raises(Protocol0Error):
        Sequence().add(wait_for_system=True, wait=1).done()


def test_async_callback_execution_order():
    # type: () -> None
    make_protocol0()
    test_res = []

    # noinspection PyClassHasNoInit
    class Example:
        @has_callback_queue()
        def listener(self):
            # type: () -> Sequence
            # noinspection PyShadowingNames
            seq = Sequence()
            seq.add(lambda: test_res.append(0), name="append 0")
            seq.add(wait=1)
            seq.add(lambda: test_res.append(1), name="append 1")
            return seq.done()

    obj = Example()

    seq = Sequence()
    seq.add(nop, complete_on=obj.listener, name="waiting for obj.listener")
    seq.add(lambda: test_res.append(2), name="append 2")
    seq.add(nop, name="after listener step")

    def check_res():
        # type: () -> None
        assert test_res == [0, 1, 2]

    seq.add(check_res)
    seq.done()

    obj.listener()


def test_wait_for_event():
    test_res = []

    seq = Sequence()
    seq.add(wait_for_event=BarEndingEvent, name="event wait seq 1")
    seq.add(lambda: test_res.append(False), name="appending res seq 1")
    seq.done()

    assert test_res == []
    seq._cancel()

    seq2 = Sequence()
    seq2.add(wait_for_event=BarEndingEvent, name="event wait seq 2")
    seq2.add(lambda: test_res.append(True), name="appending res seq 2")
    seq2.done()

    DomainEventBus.notify(BarEndingEvent())

    assert test_res == [True]


def test_wait_for_events():
    test_res = []

    def inner_seq():
        seq = Sequence()
        seq.add(wait_for_events=[BarEndingEvent, SongStoppedEvent])
        seq.add(lambda: test_res.append(True))
        return seq.done()

    seq = inner_seq()
    assert test_res == []
    seq._cancel()

    inner_seq()
    DomainEventBus.notify(BarEndingEvent())

    assert test_res == [True]

    inner_seq()
    DomainEventBus.notify(SongStoppedEvent())

    assert test_res == [True, True]


def test_cancel():
    test_res = []
    seq = Sequence()
    # seq.add(seq._cancel)
    seq.add(lambda: test_res.append(True))
    seq.done()

    assert test_res == []
