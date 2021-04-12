import sys

from a_protocol_0 import Protocol0, EmptyModule
from a_protocol_0.config import Config
from a_protocol_0.enums.LogLevelEnum import LogLevelEnum
from a_protocol_0.sequence.Sequence import Sequence

sys.dont_write_bytecode = True
sys.path.insert(0, "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts")

p0 = Protocol0(EmptyModule(is_false=False), init_song=False)
Sequence.DEBUG_MODE = False
Sequence.SILENT_MODE = True

Config.LOG_LEVEL = LogLevelEnum.ERROR
