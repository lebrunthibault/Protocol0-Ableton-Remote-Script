from collections import namedtuple

from protocol0.infra.scheduler.BeatTime import BeatTime
from protocol0.tests.domain.fixtures.p0 import make_protocol0
from protocol0.tests.domain.fixtures.song import AbletonSong


def test_beat_time_simple():
    make_protocol0()
    beat_time = BeatTime.make_from_beat_offset(1)
    assert beat_time.bars == 1
    assert beat_time.beats == 2
    assert beat_time._sixteenths == 1
    assert beat_time._ticks == 1


def test_beat_time_simple_2():
    make_protocol0()
    beat_time = BeatTime.make_from_beat_offset(8)
    assert beat_time.bars == 3
    assert beat_time.beats == 1
    assert beat_time._sixteenths == 1
    assert beat_time._ticks == 1

    beats_song_time = namedtuple("beats_song_time", ["bars", "beats", "sub_division", "ticks"])
    get_current_beats_song_time = AbletonSong.get_current_beats_song_time
    AbletonSong.get_current_beats_song_time = lambda s: beats_song_time(1, 3, 1, 5)
    beat_time = BeatTime.make_from_beat_offset(8)
    assert beat_time.bars == 3
    assert beat_time.beats == 3
    assert beat_time._sixteenths == 1
    assert beat_time._ticks == 5
    AbletonSong.get_current_beats_song_time = get_current_beats_song_time


def test_beat_time_float():
    make_protocol0()
    beat_time = BeatTime.make_from_beat_offset(1.75)
    assert beat_time.bars == 1
    assert beat_time.beats == 2
    assert beat_time._sixteenths == 4
    assert beat_time._ticks == 1


def test_beat_time_is_after():
    make_protocol0()
    beat_time = BeatTime.make_from_beat_offset(1)
    beat_time_same = BeatTime.make_from_beat_offset(1)
    beat_time_future = BeatTime.make_from_beat_offset(2)
    assert beat_time_same == beat_time
    assert beat_time_future._to_tick_count > beat_time._to_tick_count
    assert beat_time_future > beat_time
    assert beat_time < beat_time_future
    assert beat_time <= beat_time_same
    assert beat_time >= beat_time_same
