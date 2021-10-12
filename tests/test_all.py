import os
import sys

import _Framework.ControlSurface
from protocol0 import EmptyModule, create_instance
from protocol0.config import Config
from protocol0.utils.timeout import TimeoutLimit

sys.dont_write_bytecode = True  # noqa
p0 = create_instance(EmptyModule(is_false=False))
_Framework.ControlSurface.get_control_surfaces = lambda: [p0]

debug = os.getenv("DEBUG_TESTS", "False").lower() == "true"

Config.SEQUENCE_DEBUG = debug
TimeoutLimit.TICKS_COUNT = 1
