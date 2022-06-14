from protocol0.domain.shared.decorators import throttle


def test_throttle():
    def func(val):
        print("Real exec : %s" % val)
        return val + 10

    t = throttle(100)(func)

    for i in range(5):
        res = t(i)
        assert res == 10
