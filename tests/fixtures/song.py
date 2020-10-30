from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song

class AbletonSong:
    @property
    def tracks(self):
        return []

@pytest.fixture
def empty_song():
    return Song(AbletonSong())