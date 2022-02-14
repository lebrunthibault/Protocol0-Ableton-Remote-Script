from typing import TYPE_CHECKING, Callable

import protocol0.application.control_surface.group as group_package
from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.shared.utils import import_package

if TYPE_CHECKING:
    from protocol0.application.Container import Container
    from protocol0.domain.lom.song.Song import Song


class ActionGroupFactory(object):
    @classmethod
    def create_action_groups(cls, container, song, component_guard):
        # type: (Container, Song, Callable) -> None
        import_package(group_package)
        group_classes = ActionGroupMixin.__subclasses__()

        for group_class in group_classes:
            group_class(container, song, component_guard).configure()
