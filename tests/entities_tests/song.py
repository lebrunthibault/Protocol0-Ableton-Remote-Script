from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.song import make_song


def test_song_empty():
    # type: () -> None
    song = make_song()
    assert len(song.tracks) == 0
    assert song.selected_track is None


def test_song_simpler_track():
    # type: () -> None
    song = make_song(count_simple_tracks=1)
    assert len(song.tracks) == 1
    assert song.selected_track.is_simpler
    assert song.selected_track.index == 0

    song = make_song(count_simple_tracks=3)
    assert len(song.tracks) == 3
    assert song.selected_track.is_simpler
    assert song.selected_track.index == 0
