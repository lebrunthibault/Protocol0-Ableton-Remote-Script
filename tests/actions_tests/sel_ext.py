from a_protocol_0.lom.Song import Song


def test_song_group_track_next_ext(base_song):
    # type: (Song) -> None
    base_song.selected_track = base_song.tracks[3]
    base_song.current_track.action_sel()
    assert base_song.tracks[4].arm is True
    assert base_song.tracks[5].arm is True

    base_song.selected_track = base_song.tracks[6]
    assert base_song.tracks[6].is_folded
    base_song.current_track.action_sel()
    assert not base_song.tracks[6].is_folded
