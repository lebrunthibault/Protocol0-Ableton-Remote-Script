import pytest

from a_protocol_0.tests.fixtures.song import make_song


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
    assert song.selected_track.index == 3
    song.scroll_tracks(True)
    assert song.selected_track.index == 6
    song.scroll_tracks(True)
    assert song.selected_track.index == 0


def test_song_group_tracks_simpler_tracks_next_ext():
    # type: () -> None
    song = make_song(count_group_tracks=3, count_simple_tracks=2)
    song.scroll_tracks(True)
    assert song.selected_track.index == 3
    song.scroll_tracks(True)
    assert song.selected_track.index == 6
    song.scroll_tracks(True)
    assert song.selected_track.index == 9
    song.scroll_tracks(True)
    assert song.selected_track.index == 10
    song.scroll_tracks(True)
    assert song.selected_track.index == 0
