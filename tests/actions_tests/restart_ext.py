from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.song import make_song


def test_song_empty_restart_ext():
    # type: () -> None
    song = make_song()
    assert song.action_restart == ""
