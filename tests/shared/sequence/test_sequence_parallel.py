from __future__ import print_function

from functools import partial

from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.sequence.Sequence import Sequence


def test_sequence_parallel():
    # type: () -> None
    test_res = []

    def inner_seq(val):
        # type: (int) -> Sequence
        # noinspection PyShadowingNames
        seq = Sequence()

        test_res.append(val)
        seq.defer()
        seq.add(lambda: test_res.append(val + 1))

        return seq.done()

    def check_res():
        # type: () -> None
        assert test_res == [0, 2, 1, 3, 4]

    seq = Sequence()
    seq.add([partial(inner_seq, 0), partial(inner_seq, 2)])
    seq.add(lambda: test_res.append(4))
    seq.add(check_res)
    seq.done()

    assert test_res == [0, 2]


def test_sequence_parallel_wait_for_event_match():
    test_res = []

    class TestEvent(object):
        def __init__(self, value):
            # type: (int) -> None
            self.value = value

        def target(self):
            # type: () -> int
            return self.value

    def inner_sequence(value):
        # type: (int) -> Sequence
        inner_seq = Sequence()
        inner_seq.wait_for_event(TestEvent, value)
        inner_seq.add(lambda: test_res.append(value))
        return inner_seq.done()

    input_data = range(0, 2)
    seq = Sequence()
    seq.add([partial(inner_sequence, i) for i in input_data])
    seq.wait_for_event(TestEvent, 2)
    seq.done()
    assert test_res == []

    for i in input_data:
        DomainEventBus.emit(TestEvent(i))

    assert test_res == list(input_data)
    seq._cancel()
