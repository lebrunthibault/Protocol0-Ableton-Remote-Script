import sys

from protocol0.application.faderfox.ActionGroupFactory import ActionGroupFactory
from protocol0.domain.shared.utils import nop
from protocol0.shared.Logger import Logger

sys.dont_write_bytecode = True  # noqa

# hide logs
Logger.log_dev = classmethod(nop)
Logger.log_info = classmethod(nop)
Logger.log_warning = classmethod(nop)

# remove this until fixtures are thorough
ActionGroupFactory.create_action_groups = classmethod(nop)
