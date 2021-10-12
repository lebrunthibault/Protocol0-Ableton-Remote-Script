import pytest

from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import has_callback_queue
from protocol0.utils.utils import nop


def test_sanity_checks():
    # type: () -> None
    seq = Sequence(silent=True)
    seq.done()
    assert seq.terminated

    with pytest.raises(Exception):
        seq.add(wait=1)

    with pytest.raises(Exception):
        Sequence(silent=True).done().done()


def test_state_machine():
    # type: () -> None
    seq = Sequence(silent=True)
    seq.dispatch("start")

    # no error only log
    seq.dispatch("start")

    # no error only log
    seq = Sequence(silent=True)
    seq.terminate()
    seq.dispatch("start")


def test_error_no_timeout():
    # type: () -> None
    seq = Sequence(silent=True)
    seq.add(nop, complete_on=lambda: False, name="timeout step", check_timeout=0)
    seq.add(lambda: 1, name="unreachable step")
    seq.done()

    assert seq.errored


def test_callback_timeout():
    # type: () -> None
    # noinspection PyClassHasNoInit
    class Example:
        @has_callback_queue()
        def listener(self):
            # type: () -> None
            pass

    obj = Example()

    seq = Sequence(silent=True)
    seq.add(nop, complete_on=obj.listener, name="timeout step", check_timeout=1)
    seq.add(nop, name="unreachable step")
    seq.done()
    obj.listener()

    # because complete_on defers
    assert not seq.terminated


def test_async_callback_execution_order():
    # type: () -> None
    test_res = []

    # noinspection PyClassHasNoInit
    class Example:
        @has_callback_queue()
        def listener(self):
            # type: () -> Sequence
            # noinspection PyShadowingNames
            seq = Sequence(silent=True)
            seq.add(lambda: test_res.append(0), name="append 0")
            seq.add(wait=1)
            seq.add(lambda: test_res.append(1), name="append 1")
            return seq.done()

    obj = Example()

    seq = Sequence(silent=True)
    seq.add(nop, complete_on=obj.listener, name="waiting for obj.listener", check_timeout=2)
    seq.add(lambda: test_res.append(2), name="append 2")
    seq.add(nop, name="after listener step")

    def check_res():
        # type: () -> None
        assert test_res == [0, 1, 2]

    seq.add(check_res)
    seq.done()

    obj.listener()
