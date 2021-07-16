from protocol0.utils.math_utils import linear, exp_curve


def test_linear():
    # type: () -> None
    x1 = 0
    x2 = 2
    y1 = 0
    y2 = 20

    x = 1
    assert linear(x1=x1, y1=y1, x2=x2, y2=y2, x=x) == 10


def test_exp():
    # type: () -> None
    x1 = 0
    x2 = 2
    y1 = 0
    y2 = 20

    x = 1

    for alpha in [0, 1, 2, 3, 4, 5, 10]:
        assert y1 < exp_curve(x1=x1, y1=y1, x2=x2, y2=y2, x=x, alpha=alpha) < y2
