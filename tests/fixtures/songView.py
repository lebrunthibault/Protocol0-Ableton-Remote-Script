import pytest

class AbletonSongView:
    def __init__(self, selected_track):
        self.selected_track = selected_track

@pytest.fixture
def ableton_song_view(selected_track = None):
    return AbletonSongView(selected_track)
