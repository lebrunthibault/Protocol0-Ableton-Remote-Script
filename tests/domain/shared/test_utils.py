from protocol0.domain.shared.ValueScroller import ValueScroller


def test_scroll_values():
    assert 3 == ValueScroller.scroll_values([1, 2, 3], 2, True)
    assert 1 == ValueScroller.scroll_values([1, 2, 3], 2, False)
    assert 1 == ValueScroller.scroll_values([1, 2, 3], 3, True)
    assert 3 == ValueScroller.scroll_values([1, 2, 3], 3, True, rotate=False)
