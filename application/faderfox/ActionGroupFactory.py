from typing import TYPE_CHECKING

from protocol0.application.faderfox.group.ActionGroupData import ActionGroupData
from protocol0.application.faderfox.group.ActionGroupFix import ActionGroupFix
from protocol0.application.faderfox.group.ActionGroupLog import ActionGroupLog
from protocol0.application.faderfox.group.ActionGroupMain import ActionGroupMain
from protocol0.application.faderfox.group.ActionGroupMix import ActionGroupMix
from protocol0.application.faderfox.group.ActionGroupPreset import ActionGroupPreset
from protocol0.application.faderfox.group.ActionGroupSet import ActionGroupSet
from protocol0.application.faderfox.group.ActionGroupTest import ActionGroupTest

if TYPE_CHECKING:
    from protocol0.application.Container import Container


class ActionGroupFactory(object):
    @classmethod
    def create_action_groups(cls, container):
        # type: (Container) -> None
        ActionGroupData(container).configure()
        ActionGroupFix(container).configure()
        ActionGroupLog(container).configure()
        ActionGroupMain(container).configure()
        ActionGroupMix(container).configure()
        ActionGroupPreset(container).configure()
        ActionGroupSet(container).configure()
        ActionGroupTest(container).configure()
