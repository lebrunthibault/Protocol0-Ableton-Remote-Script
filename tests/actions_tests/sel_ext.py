from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.simpleTrack import get_track


def test_song_group_track_next_ext(base_song):
    # type: (Song) -> None
    get_track(base_song.tracks[3]).action_sel()
    assert base_song.tracks[4].arm is True
    assert base_song.tracks[5].arm is True
    get_track(base_song.tracks[6]).action_sel()
    assert base_song.tracks[6].is_folded
    get_track(base_song.tracks[6]).action_sel()
    assert not base_song.tracks[6].is_folded
