from _Framework.ControlSurface import ControlSurface
from typing import Any

from protocol0.application.CommandBus import CommandBus
from protocol0.application.Container import Container
from protocol0.application.command.InitializeSongCommand import InitializeSongCommand
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.logging.Logger import Logger


class Protocol0(ControlSurface):
    def __init__(self, c_instance=None):
        # type: (Any) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)

        # noinspection PyBroadException
        try:
            Container(self)
        except Exception:
            DomainEventBus.emit(ErrorRaisedEvent())
            return

        CommandBus.dispatch(InitializeSongCommand())

        Logger.info("Protocol0 script loaded")
