import pytest

from ..fixtures.song import make_song, select_song_track


def test_song_empty_next_ext():
    # type: () -> None
    song = make_song()
    with pytest.raises(Exception):
        song.action_next(True)


def test_song_simpler_track_next_ext():
    # type: () -> None
    song = make_song(count_simple_tracks=1)
    assert song.action_next(True) == "; 1/sel"
    assert song.action_next(True) == "; 1/sel"
    assert song.action_next(False) == "; 1/sel"


def test_song_simpler_tracks_next_ext():
    # type: () -> None
    song = make_song(count_simple_tracks=3)
    assert song.action_next(True) == "; 2/sel"
    select_song_track(song, 2)
    print(song.action_next(True))
    assert song.action_next(True) == "; 3/sel"
    # assert song.action_next(True) == "; 1/sel"
    # assert song.action_next(False) == "; 3/sel"
    # assert song.action_next(False) == "; 2/sel"
    # assert song.action_next(False) == "; 1/sel"
