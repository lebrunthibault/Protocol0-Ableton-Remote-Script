from typing import Callable

import protocol0.application.control_surface.group as group_package
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.shared.utils.utils import import_package


class ActionGroupFactory(object):
    @classmethod
    def create_action_groups(cls, container, component_guard):
        # type: (ContainerInterface, Callable) -> None
        import_package(group_package)
        group_classes = ActionGroupInterface.__subclasses__()

        for group_class in group_classes:
            if group_class.CHANNEL is not None:
                group_class(container, component_guard).configure()
