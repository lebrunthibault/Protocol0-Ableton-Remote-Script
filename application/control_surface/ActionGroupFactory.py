from typing import TYPE_CHECKING, Callable

from protocol0.application.control_surface.group.ActionGroupData import ActionGroupData
from protocol0.application.control_surface.group.ActionGroupFix import ActionGroupFix
from protocol0.application.control_surface.group.ActionGroupLog import ActionGroupLog
from protocol0.application.control_surface.group.ActionGroupMain import ActionGroupMain
from protocol0.application.control_surface.group.ActionGroupMix import ActionGroupMix
from protocol0.application.control_surface.group.ActionGroupPreset import ActionGroupPreset
from protocol0.application.control_surface.group.ActionGroupSet import ActionGroupSet
from protocol0.application.control_surface.group.ActionGroupTest import ActionGroupTest

if TYPE_CHECKING:
    from protocol0.application.Container import Container
    from protocol0.domain.lom.song.Song import Song


class ActionGroupFactory(object):
    @classmethod
    def create_action_groups(cls, container, song, component_guard):
        # type: (Container, Song, Callable) -> None
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
            group(container, song, component_guard).configure()
