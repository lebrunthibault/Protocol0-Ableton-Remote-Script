from functools import partial

from protocol0.domain.shared.utils.func import is_func_equal


def test_func_equal():
    def f():
        pass

    assert is_func_equal(f, f)

    class T(object):
        def m(self):
            pass

    t = T()
    assert is_func_equal(t.m, t.m)

    p1 = partial(t.m)
    p2 = partial(t.m)

    assert is_func_equal(p1, p2)


class Test(object):
    def m(self):
        pass


def test_func_equal_method():
    t1, t2 = Test(), Test()
    assert not is_func_equal(t1.m, t2.m)
    assert is_func_equal(t1.m, t2.m, compare_methods=True)
