import pytest

class AbletonSongView:
    def __init__(self, selected_track=None):
        self.selected_track = selected_track

@pytest.fixture
def ableton_song_view():
    return AbletonSongView()
