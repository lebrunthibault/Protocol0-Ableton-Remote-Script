from types import MethodType

from typing import Any

from _Framework.ControlSurface import ControlSurface
from protocol0.application.CommandBus import CommandBus
from protocol0.application.Container import Container
from protocol0.application.command.InitializeSongCommand import InitializeSongCommand
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.shared.logging.Logger import Logger


class Protocol0(ControlSurface):
    def __init__(self, c_instance=None):
        # type: (Any) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)

        # # stop log duplication
        # self._c_instance.log_message = MethodType(lambda s, message: None, self._c_instance)  # noqa

        # noinspection PyBroadException
        try:
            Container(self)
        except Exception:
            DomainEventBus.notify(ErrorRaisedEvent())
            return

        CommandBus.dispatch(InitializeSongCommand())

        Logger.log_info("Protocol0 script loaded")
