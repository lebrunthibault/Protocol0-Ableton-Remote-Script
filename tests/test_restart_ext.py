import sys
import os


sys.dont_write_bytecode = True
sys.path.insert(0, "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts")
init_file = "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\ClyphX_Pro\__init__.py"
with open(init_file, "a"):
    from .fixtures import *

os.remove(init_file)
from shutil import copyfile
copyfile("C:\\Users\\thiba\\Google Drive\\music\\software presets\\clyphx pro\\Manual Setup\\MIDI Remote Scripts\\ClyphX_Pro\\__init__.pyc", "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\ClyphX_Pro\__init__.pyc")

def test_song_empty(song_empty):
    assert len(song_empty.tracks) == 0

def test_song_empty_restart_ext(song_empty):
    assert song_empty.action_restart == ""

def test_song_empty_next_ext(song_empty):
    with pytest.raises(Exception):
        song_empty.action_next(True)
