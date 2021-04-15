from a_protocol_0.sequence.Sequence import Sequence
# noinspection PyUnresolvedReferences
from a_protocol_0.tests.test_all import p0


def test_do_if():
    class Obj:
        a = 2
    obj = Obj()
    seq = Sequence()
    seq.add(lambda: setattr(obj, "a", 3), do_if=lambda: obj.a == 0)
    seq.add(lambda: setattr(obj, "a", 4), do_if_not=lambda: obj.a == 0)
    seq.done()
    assert seq.terminated
    assert obj.a == 4


def test_return_if():
    class Obj:
        a = 2
    obj = Obj()
    seq = Sequence(silent=True)
    seq.add(lambda: setattr(obj, "a", 3), return_if_not=lambda: obj.a != 0)
    seq.add(lambda: setattr(obj, "a", 4), return_if=lambda: obj.a != 0)
    seq.add(lambda: setattr(obj, "a", 5))
    seq.done()
    assert seq.terminated
    assert obj.a == 3
