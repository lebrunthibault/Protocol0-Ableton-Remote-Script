import sys

import _Framework.ControlSurface
from protocol0 import EmptyModule, create_instance
from protocol0.config import Config
from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.utils.timeout import TimeoutLimit

sys.dont_write_bytecode = True  # noqa
p0 = create_instance(EmptyModule(name="c_instance", is_false=False))
_Framework.ControlSurface.get_control_surfaces = lambda: [p0]

Config.SEQUENCE_DEBUG = True
TimeoutLimit.TICKS_COUNT = 1
Config.ABLETON_SESSION_TYPE = AbletonSessionTypeEnum.TEST
