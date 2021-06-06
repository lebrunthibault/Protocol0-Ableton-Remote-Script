import os
import sys

from a_protocol_0 import Protocol0, EmptyModule
from a_protocol_0.config import Config
from a_protocol_0.enums.LogLevelEnum import LogLevelEnum
from a_protocol_0.utils.timeout import TimeoutLimit

sys.dont_write_bytecode = True  # noqa
p0 = Protocol0(EmptyModule(is_false=False), init_song=False)

debug = os.getenv("DEBUG_TESTS", "False").lower() == "true"

Config.SEQUENCE_DEBUG_MODE = debug
Config.SEQUENCE_SILENT_MODE = not debug
TimeoutLimit.TICKS_COUNT = 1

Config.LOG_LEVEL = LogLevelEnum.DEV if debug else LogLevelEnum.DISABLED
