import sys
from threading import Timer

from typing import Callable

from protocol0.application.control_surface.ActionGroupFactory import ActionGroupFactory
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import nop
from protocol0.shared.logging.Logger import Logger

sys.dont_write_bytecode = True  # noqa

# hide logs
Logger.log_dev = classmethod(nop)
Logger.log_info = classmethod(nop)
Logger.log_warning = classmethod(nop)


def wait(_, tick_count, callback):
    # type: (Scheduler, int, Callable) -> None
    Timer(tick_count / 100, callback).start()


Scheduler.wait = classmethod(wait)
Scheduler.defer = classmethod(lambda func: func())

# remove this until fixtures are thorough
ActionGroupFactory.create_action_groups = classmethod(nop)
