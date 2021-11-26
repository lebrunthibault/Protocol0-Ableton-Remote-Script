from protocol0.sequence.Sequence import Sequence


def test_do_if():
    # type: () -> None
    # noinspection PyClassHasNoInit
    class Obj:
        a = 2

    obj = Obj()
    seq = Sequence()
    seq.add(lambda: setattr(obj, "a", 3), do_if=lambda: obj.a == 0)
    seq.add(lambda: setattr(obj, "a", 4), do_if=lambda: obj.a != 0)
    seq.done()
    assert seq.terminated
    assert obj.a == 4
