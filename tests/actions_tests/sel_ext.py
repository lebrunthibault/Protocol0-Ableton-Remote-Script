from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


def test_song_group_track_next_ext(base_song):
    # type: (Song) -> None
    base_song.view.selected_track = base_song.tracks[9]
