from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures import AbletonSong, simpler_track
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.songView import AbletonSongView


def test_simpler_track(ableton_song_view):
    # type: (AbletonSongView) -> None
    song = Song(AbletonSong([], ableton_song_view))
    track = simpler_track(song)
    song.tracks = [track]
    assert track == track
