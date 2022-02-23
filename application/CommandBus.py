from typing import Dict, Type, Optional, TYPE_CHECKING

import protocol0.application.command as command_package
import protocol0.application.command_handler as command_handler_package
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import import_package
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.shared.UndoFacade import UndoFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song

CommandMapping = Dict[Type[SerializableCommand], Type[CommandHandlerInterface]]


class CommandBus(object):
    _INSTANCE = None  # type: Optional[CommandBus]

    def __init__(self, container, song):
        # type: (ContainerInterface, Song) -> None
        CommandBus._INSTANCE = self
        self._container = container
        self._song = song
        self._command_mapping = self._create_command_mapping()

    def _create_command_mapping(self):
        # type: () -> CommandMapping
        import_package(command_package)
        import_package(command_handler_package)

        handler_classes = CommandHandlerInterface.__subclasses__()
        command_classes = SerializableCommand.__subclasses__()

        handler_names_to_class = {handler_class.__name__: handler_class for handler_class in handler_classes}

        mapping = {}  # type: CommandMapping
        # matching on class name
        for command_class in command_classes:
            handler_class_name = command_class.__name__ + "Handler"
            if handler_class_name not in handler_names_to_class:
                raise Protocol0Error("Couldn't find matching handler for %s" % command_class)

            mapping[command_class] = handler_names_to_class[handler_class_name]

        return mapping

    @classmethod
    def dispatch(cls, command):
        # type: (SerializableCommand) -> None
        cls._INSTANCE._dispatch_command(command)

    def _dispatch_command(self, command):
        # type: (SerializableCommand) -> None
        handler = self._command_mapping[command.__class__](self._container, self._song)
        UndoFacade.begin_undo_step()
        handler.handle(command)
