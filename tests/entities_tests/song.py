from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


def test_song_empty(song_empty):
    # type: (Song) -> None
    assert len(song_empty.tracks) == 0
    assert song_empty.selected_track is None

def test_song_simpler_track(song_simpler_track):
    # type: (Song) -> None
    assert len(song_simpler_track.tracks) == 1
    assert song_simpler_track.selected_track.is_simpler
