import pytest
import sys
import os

sys.dont_write_bytecode = True
sys.path.insert(0, "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts")
init_file = "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\ClyphX_Pro\__init__.py"
with open(init_file, "a"):
    from .fixtures.song import empty_song

os.remove(init_file)

def test_default_song(empty_song):
    assert len(empty_song.tracks) == 0