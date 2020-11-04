import os

init_file = "C:\\ProgramData\\Ableton\\Live 10 Suite\\Resources\\MIDI Remote Scripts\\ClyphX_Pro\\__init__.py"

os.remove(init_file)
from shutil import copyfile

copyfile(
    "C:\\Users\\thiba\\Google Drive\\music\\software presets\\clyphx pro\\Manual Setup\\MIDI Remote Scripts\\ClyphX_Pro\\__init__.pyc",
    "C:\\ProgramData\\Ableton\\Live 10 Suite\\Resources\\MIDI Remote Scripts\\ClyphX_Pro\\__init__.pyc")
