import sys

import _Framework.ControlSurface
from protocol0 import EmptyModule, create_instance, Protocol0
from protocol0.application.config import Config
from protocol0.application.service.ErrorManager import ErrorManager
from protocol0.domain.sequence.TimeoutLimit import TimeoutLimit
from protocol0.domain.shared.utils import nop
from protocol0.infra.SongDataManager import SongDataManager
from protocol0.shared.Logger import Logger

sys.dont_write_bytecode = True  # noqa
Protocol0.start = nop
SongDataManager.restore_data = nop
Logger.log_info = classmethod(nop)
Logger.log_warning = classmethod(nop)
ErrorManager.handle_error = nop
p0 = create_instance(EmptyModule(name="c_instance", is_false=False))
_Framework.ControlSurface.get_control_surfaces = lambda: [p0]

Config.SEQUENCE_DEBUG = True
TimeoutLimit.TICKS_COUNT = 1
