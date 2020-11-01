from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


def test_song_group_track_next_ext(base_song):
    # type: (Song) -> None
    print(base_song.tracks[4].action_sel)
    assert " 5/fold off; 6/arm off; 7/arm on; 8/arm on;" in base_song.tracks[4].action_sel
    assert base_song.tracks[8].action_sel == "; 9/fold on"
    base_song.tracks[8].track.fold_state = True
    assert base_song.tracks[8].action_sel == "; 9/fold off"
    assert base_song.tracks[9].action_sel == "; 10/sel"
