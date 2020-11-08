import pytest

from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.song import make_song, select_song_track


def test_song_empty_next_ext():
    # type: () -> None
    song = make_song()
    with pytest.raises(Exception):
        song.scroll_tracks(True)


def test_song_simpler_track_next_ext():
    # type: () -> None
    song = make_song(count_simple_tracks=1)
    assert song.selected_track.index == 0
    song.scroll_tracks(True)
    assert song.selected_track.index == 0
    song.scroll_tracks(True)
    assert song.selected_track.index == 0
    song.scroll_tracks(False)
    assert song.selected_track.index == 0


def test_song_simpler_tracks_next_ext():
    # type: () -> None
    song = make_song(count_simple_tracks=3)
    song.scroll_tracks(True)
    assert song.selected_track.index == 1
    song.scroll_tracks(True)
    assert song.selected_track.index == 2
    song.scroll_tracks(True)
    assert song.selected_track.index == 0
    song.scroll_tracks(False)
    assert song.selected_track.index == 2
    song.scroll_tracks(False)
    assert song.selected_track.index == 1
    song.scroll_tracks(False)
    assert song.selected_track.index == 0


def test_song_group_track_next_ext():
    # type: () -> None
    song = make_song(count_group_tracks=1)
    song.scroll_tracks(True)
    assert song.selected_track.index == 0
    song.scroll_tracks(True)
    assert song.selected_track.index == 0


def test_song_group_tracks_next_ext():
    # type: () -> None
    song = make_song(count_group_tracks=3)
    song.scroll_tracks(True)
    assert song.selected_track.index == 4
    song.scroll_tracks(True)
    assert song.selected_track.index == 8
    song.scroll_tracks(True)
    assert song.selected_track.index == 0


def test_song_group_tracks_simpler_tracks_next_ext():
    # type: () -> None
    song = make_song(count_group_tracks=3, count_simple_tracks=2)
    song.scroll_tracks(True)
    assert song.selected_track.index == 4
    song.scroll_tracks(True)
    assert song.selected_track.index == 8
    song.scroll_tracks(True)
    assert song.selected_track.index == 12
    song.scroll_tracks(True)
    assert song.selected_track.index == 13
    song.scroll_tracks(True)
    assert song.selected_track.index == 0
