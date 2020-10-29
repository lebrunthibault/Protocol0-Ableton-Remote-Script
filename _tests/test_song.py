import pytest
import sys

init_file = "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\ClyphX_Pro\__init__.py"

sys.path.insert(0, "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts")
from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


class AbletonSong:
    @property
    def tracks(self):
        return []

@pytest.fixture
def empty_song():
    return Song(AbletonSong())

def test_default_song(empty_song):
    assert len(empty_song.tracks) == 0