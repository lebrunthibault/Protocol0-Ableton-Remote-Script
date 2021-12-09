import pytest

from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import has_callback_queue
from protocol0.utils.utils import nop


def test_sanity_checks():
    # type: () -> None
    seq = Sequence(silent=True)
    seq.add([])
    seq.done()
    assert seq.terminated

    with pytest.raises(Exception):
        seq.add(wait=1)

    with pytest.raises(Exception):
        Sequence(silent=True).done().done()

    with pytest.raises(Exception):
        Sequence(silent=True).add(wait=1, complete_on=lambda: True).done()

    with pytest.raises(Exception):
        Sequence(silent=True).add(wait_for_system=True, wait=1).done()


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

    seq = Sequence()
    seq.add(nop, complete_on=obj.listener, name="waiting for obj.listener", check_timeout=3)
    seq.add(lambda: test_res.append(2), name="append 2")
    seq.add(nop, name="after listener step")

    def check_res():
        # type: () -> None
        assert test_res == [0, 1, 2]

    seq.add(check_res)
    seq.done()

    obj.listener()
