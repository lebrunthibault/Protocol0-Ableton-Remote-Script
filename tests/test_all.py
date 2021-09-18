import os
import sys

from protocol0 import Protocol0, EmptyModule, create_instance
from protocol0.config import Config
from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.utils.timeout import TimeoutLimit
import _Framework.ControlSurface


sys.dont_write_bytecode = True  # noqa
p0 = create_instance(EmptyModule(is_false=False))
_Framework.ControlSurface.get_control_surfaces = lambda: [p0]

debug = os.getenv("DEBUG_TESTS", "False").lower() == "true"

Config.SEQUENCE_DEBUG = debug
TimeoutLimit.TICKS_COUNT = 1

Config.LOG_LEVEL = LogLevelEnum.DEV if debug else LogLevelEnum.DISABLED
