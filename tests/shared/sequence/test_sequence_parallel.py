from __future__ import print_function

from functools import partial

from protocol0.shared.sequence.Sequence import Sequence


def test_sequence_parallel():
    # type: () -> None
    test_res = []

    def inner_seq(val):
        # type: (int) -> Sequence
        # noinspection PyShadowingNames
        seq = Sequence()

        test_res.append(val)
        seq.wait(100)
        seq.add(lambda: test_res.append(val + 1))

        return seq.done()

    def check_res():
        # type: () -> None
        assert test_res == [0, 2, 1, 3]

    seq = Sequence()
    seq.add([partial(inner_seq, 0), partial(inner_seq, 2)])
    seq.add(check_res)
    seq.done()
