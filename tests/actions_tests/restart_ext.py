from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


def test_song_empty_restart_ext(song_empty):
    # type: (Song) -> None
    assert song_empty.action_restart == ""
