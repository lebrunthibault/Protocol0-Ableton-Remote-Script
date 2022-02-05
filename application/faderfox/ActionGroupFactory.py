from protocol0.application.faderfox.group.ActionGroupData import ActionGroupData
from protocol0.application.faderfox.group.ActionGroupFix import ActionGroupFix
from protocol0.application.faderfox.group.ActionGroupLog import ActionGroupLog
from protocol0.application.faderfox.group.ActionGroupMain import ActionGroupMain
from protocol0.application.faderfox.group.ActionGroupMix import ActionGroupMix
from protocol0.application.faderfox.group.ActionGroupPreset import ActionGroupPreset
from protocol0.application.faderfox.group.ActionGroupSet import ActionGroupSet
from protocol0.application.faderfox.group.ActionGroupTest import ActionGroupTest
from protocol0.shared.Logger import Logger


class ActionGroupFactory(object):
    @classmethod
    def create_action_groups(cls):
        # type: () -> None
        Logger.log_dev("creating action groups ")
        ActionGroupData()
        ActionGroupFix()
        ActionGroupLog()
        ActionGroupMain()
        ActionGroupMix()
        ActionGroupPreset()
        ActionGroupSet()
        ActionGroupTest()
