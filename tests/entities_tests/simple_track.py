from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.song import AbletonSong, make_song


def test_simpler_track():
    # type: () -> None
    track = make_song(count_simple_tracks=1).tracks[0]
    assert track == track
