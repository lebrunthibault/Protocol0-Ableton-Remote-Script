from protocol0.domain.shared.utils import scroll_values


def test_scroll_values():
    assert 3 == scroll_values([1, 2, 3], 2, True)
    assert 1 == scroll_values([1, 2, 3], 2, False)
    assert 1 == scroll_values([1, 2, 3], 3, True)
    assert 3 == scroll_values([1, 2, 3], 3, True, rotate=False)
