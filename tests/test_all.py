import os
import sys

from protocol0 import Protocol0, EmptyModule
from protocol0.config import Config
from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.utils.timeout import TimeoutLimit

sys.dont_write_bytecode = True  # noqa
p0 = Protocol0(EmptyModule(is_false=False), test_mode=True)

debug = os.getenv("DEBUG_TESTS", "False").lower() == "true"

Config.SEQUENCE_DEBUG = debug
TimeoutLimit.TICKS_COUNT = 1

Config.LOG_LEVEL = LogLevelEnum.DEV if debug else LogLevelEnum.DISABLED
