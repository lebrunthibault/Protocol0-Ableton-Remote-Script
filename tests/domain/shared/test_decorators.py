from protocol0.domain.shared.utils.timing import throttle


def test_throttle():
    def func(val):
        return val + 10

    t = throttle(100)(func)

    for i in range(5):
        res = t(i)
        assert res == 10
