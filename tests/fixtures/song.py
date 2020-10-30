import pytest

from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.songView import AbletonSongView
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.simpleTrack import simpler_track


class AbletonSong:
    def __init__(self, tracks, view):
        self.tracks = tracks if tracks else []
        self.view = view

@pytest.fixture
def song_empty(ableton_song_view):
    # type: (AbletonSongView) -> Song
    return Song(AbletonSong([], ableton_song_view))

@pytest.fixture
def song_simpler_track(ableton_song_view):
    # type: (AbletonSongView) -> Song
    song = Song(AbletonSong([], ableton_song_view))
    track = simpler_track(song)
    song.tracks = [track]
    song.view.selected_track = track.track

    return song
