import pytest

from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import has_callback_queue
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.utils import nop
from protocol0.shared.sequence.Sequence import Sequence


def test_sanity_checks():
    # type: () -> None
    seq = Sequence()
    seq.add([])
    seq.done()
    assert seq.terminated

    with pytest.raises(AssertionError):
        seq.add(wait=1)

    with pytest.raises(Protocol0Error):
        Sequence().add(wait=1, complete_on=lambda: True).done()

    with pytest.raises(Protocol0Error):
        Sequence().add(wait_for_system=True, wait=1).done()


def test_async_callback_execution_order():
    # type: () -> None
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


def test_sequence_cancel():
    # type: () -> None
    """ A cancelled inner seq will cancel all parent sequences """
    test_res = []

    def inner_seq():
        # type: () -> Sequence
        seq = Sequence()
        return seq.done()

    seq = Sequence()
    seq.add(inner_seq)
    seq.add(lambda: test_res.append(True))
    seq.done()

    assert test_res == [True]

    test_res = []

    def inner_seq_cancel():
        # type: () -> Sequence
        seq = Sequence()
        seq.add(seq.cancel)
        return seq.done()

    seq = Sequence()
    seq.add(inner_seq_cancel)
    seq.add(lambda: test_res.append(True))
    seq.done()
    assert test_res == []
    assert seq.cancelled

    def inner_inner_seq_cancel():
        seq = Sequence()
        seq.add(inner_seq_cancel)
        return seq.done()

    seq = Sequence()
    seq.add(inner_inner_seq_cancel)
    seq.add(lambda: test_res.append(True))
    seq.done()
    assert test_res == []
    assert seq.cancelled


def test_wait_for_event():
    test_res = []

    seq = Sequence()
    seq.add(wait_for_event=BarEndingEvent)
    seq.add(lambda: test_res.append(True))
    seq.done()

    assert test_res == []
    seq.cancel()

    seq = Sequence()
    seq.add(wait_for_event=BarEndingEvent)
    seq.add(lambda: test_res.append(True))
    seq.done()

    DomainEventBus.notify(BarEndingEvent())

    assert test_res == [True]
