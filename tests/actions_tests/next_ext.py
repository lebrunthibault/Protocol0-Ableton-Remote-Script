import pytest

from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.song import make_song, select_song_track


def test_song_empty_next_ext():
    # type: () -> None
    song = make_song()
    with pytest.raises(Exception):
        song.action_next(True)


def test_song_simpler_track_next_ext():
    # type: () -> None
    song = make_song(count_simple_tracks=1)
    assert song.selected_track.index == 1
    song.action_next(True)
    assert song.selected_track.index == 1
    song.action_next(True)
    assert song.selected_track.index == 1
    song.action_next(False)
    assert song.selected_track.index == 1


def test_song_simpler_tracks_next_ext():
    # type: () -> None
    song = make_song(count_simple_tracks=3)
    song.action_next(True)
    assert song.selected_track.index == 2
    song.action_next(True)
    assert song.selected_track.index == 3
    song.action_next(True)
    assert song.selected_track.index == 1
    song.action_next(False)
    assert song.selected_track.index == 3
    song.action_next(False)
    assert song.selected_track.index == 2
    song.action_next(False)
    assert song.selected_track.index == 1


def test_song_group_track_next_ext():
    # type: () -> None
    song = make_song(count_group_tracks=1)
    assert song.action_next(True) == "; 1/sel"
    assert song.action_next(True) == "; 1/sel"
    assert song.action_next(True) == "; 1/sel"


def test_song_group_tracks_next_ext():
    # type: () -> None
    song = make_song(count_group_tracks=3)
    assert song.action_next(True) == "; 5/sel"
    select_song_track(song, 5)
    assert song.action_next(True) == "; 9/sel"
    select_song_track(song, 9)
    assert song.action_next(True) == "; 1/sel"


def test_song_group_tracks_simpler_tracks_next_ext():
    # type: () -> None
    song = make_song(count_group_tracks=3, count_simple_tracks=2)
    assert song.action_next(True) == "; 5/sel"
    select_song_track(song, 5)
    assert song.action_next(True) == "; 9/sel"
    select_song_track(song, 9)
    assert song.action_next(True) == "; 13/sel"
    select_song_track(song, 13)
    assert song.action_next(True) == "; 14/sel"
    select_song_track(song, 14)
    assert song.action_next(True) == "; 1/sel"
