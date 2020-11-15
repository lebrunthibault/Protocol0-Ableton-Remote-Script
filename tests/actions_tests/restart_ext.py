from a_protocol_0.tests.fixtures.song import make_song


def test_song_empty_restart_ext():
    # type: () -> None
    song = make_song()
    assert song.restart_set() is None
