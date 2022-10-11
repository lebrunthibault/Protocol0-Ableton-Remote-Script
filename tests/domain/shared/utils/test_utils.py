from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.utils.utils import volume_to_db, db_to_volume


def test_scroll_values():
    assert 3 == ValueScroller.scroll_values([1, 2, 3], 2, True)
    assert 1 == ValueScroller.scroll_values([1, 2, 3], 2, False)
    assert 1 == ValueScroller.scroll_values([1, 2, 3], 3, True)
    assert 3 == ValueScroller.scroll_values([1, 2, 3], 3, True, rotate=False)


def test_volume_to_db():
    measures = {
        1: 6,
        0.850000023842: 0,
        0.800000011921: -2,
        0.724942445755: -5,
        0.674942433834: -7,
        0.599999904633: -10,
        0.474942296743: -15,
        0.238438740373: -30,
        0.0346231460571: -60,
    }

    for x, y in measures.items():
        assert volume_to_db(x) - y < 0.05
        assert db_to_volume(y) - x < 0.05


# def test_volume_to_db2():
#     measures = {
#         1: 6,
#         0.850000023842: 0,
#         0.800000011921: -2,
#         0.724942445755: -5,
#         0.674942433834: -7,
#         0.599999904633: -10,
#         0.474942296743: -15,
#         0.238438740373: -30,
#         0.0346231460571: -60,
#     }
#
#     deviations = 0
#     for x, y in measures.items():
#         fx = volume_to_db(x)
#         deviations += abs(y - fx)
#         Logger.error("f(%s) = %s (-> %s)" % (x, fx, y))
#
#     Logger.error("average deviation : %s" % (deviations / len(measures)))
