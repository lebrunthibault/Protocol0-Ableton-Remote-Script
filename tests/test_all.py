import os
import sys

from a_protocol_0 import Protocol0, EmptyModule
from a_protocol_0.config import Config
from a_protocol_0.enums.LogLevelEnum import LogLevelEnum
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.timeout import TimeoutLimit

sys.dont_write_bytecode = True  # noqa
sys.path.insert(0, "C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts")

p0 = Protocol0(EmptyModule(is_false=False), init_song=False)

debug = os.getenv("DEBUG_TESTS", "False").lower() == "true"

Sequence.DEBUG_MODE = debug
Sequence.SILENT_MODE = not debug
TimeoutLimit.TICKS_COUNT = 1

Config.LOG_LEVEL = LogLevelEnum.DEV if debug else LogLevelEnum.DISABLED
