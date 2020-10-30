import pytest

from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


class AbletonSong:
    def __init__(self, tracks, view):
        self.tracks = tracks if tracks else []
        self.view = view

@pytest.fixture
def song_empty(ableton_song_view, tracks = None, selected_track = None):
    return Song(AbletonSong(tracks, ableton_song_view))

@pytest.fixture
def song_simple_track(ableton_song_view, tracks = None, selected_track = None):
    return Song(AbletonSong(tracks, ableton_song_view))
