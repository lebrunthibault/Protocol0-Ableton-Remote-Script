from protocol0.infra.scheduler.BeatTime import BeatTime
from protocol0.tests.fixtures.p0 import make_protocol0


def test_beat_time_simple():
    make_protocol0()
    beat_time = BeatTime.make_from_beat_count(1)
    assert beat_time._bars == 1
    assert beat_time.beats == 2
    assert beat_time._sixteenths == 1
    assert beat_time._ticks == 1


def test_beat_time_float():
    make_protocol0()
    beat_time = BeatTime.make_from_beat_count(1.75)
    assert beat_time._bars == 1
    assert beat_time.beats == 2
    assert beat_time._sixteenths == 4
    assert beat_time._ticks == 1


def test_beat_time_is_after():
    make_protocol0()
    beat_time = BeatTime.make_from_beat_count(1)
    beat_time_same = BeatTime.make_from_beat_count(1)
    beat_time_future = BeatTime.make_from_beat_count(2)
    assert beat_time_same == beat_time
    assert beat_time_future > beat_time
    assert beat_time < beat_time_future
    assert beat_time <= beat_time_same
    assert beat_time >= beat_time_same
