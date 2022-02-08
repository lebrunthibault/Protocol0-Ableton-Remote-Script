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
    from protocol0.domain.lom.song.Song import Song


class ActionGroupFactory(object):
    @classmethod
    def create_action_groups(cls, container, song):
        # type: (Container, Song) -> None
        groups = [
            ActionGroupData,
            ActionGroupFix,
            ActionGroupLog,
            ActionGroupMain,
            ActionGroupMix,
            ActionGroupPreset,
            ActionGroupSet,
            ActionGroupTest,
        ]

        for group in groups:
            group(container, song).configure()
