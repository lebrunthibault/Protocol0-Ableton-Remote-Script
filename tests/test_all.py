import sys
import os


sys.dont_write_bytecode = True
# sys.path.insert(0, "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts")
# print(sys.path)
# init_file = "C:\\ProgramData\\Ableton\\Live 10 Suite\\Resources\\MIDI Remote Scripts\\ClyphX_Pro\\__init__.py"
# try:
#     print("open and import")
#     with open(init_file, "a"):
from .fixtures import *

from .actions_tests import *
from .entities_tests import *
#
# finally:
#     print("clean files")
#     os.remove(init_file)
#     from shutil import copyfile
#     copyfile("C:\\Users\\thiba\\Google Drive\\music\\software presets\\clyphx pro\\Manual Setup\\MIDI Remote Scripts\\ClyphX_Pro\\__init__.pyc", "C:\\ProgramData\\Ableton\\Live 10 Suite\\Resources\\MIDI Remote Scripts\\ClyphX_Pro\\__init__.pyc")
