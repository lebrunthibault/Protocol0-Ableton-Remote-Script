import time

from typing import Dict, Type, Optional, TYPE_CHECKING

import protocol0.application.command as command_package
import protocol0.application.command_handler as command_handler_package
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import import_package
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song

CommandMapping = Dict[Type[SerializableCommand], Type[CommandHandlerInterface]]


class CommandBus(object):
    _DEBUG = True
    _INSTANCE = None  # type: Optional[CommandBus]

    def __init__(self, container, song):
        # type: (ContainerInterface, Song) -> None
        CommandBus._INSTANCE = self
        self._container = container
        self._song = song
        self._command_mapping = self._create_command_mapping()
        self._last_command = None  # type: Optional[SerializableCommand]
        self._last_command_processed_at = None  # type: Optional[float]

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
        # type: (SerializableCommand) -> Optional[Sequence]
        return cls._INSTANCE._dispatch_command(command)

    @handle_error
    def _dispatch_command(self, command):
        # type: (SerializableCommand) -> Optional[Sequence]
        if self._is_duplicate_command(command):
            Backend.client().show_warning("skipping duplicate command: please reload the set")
            return None

        self._last_command = command
        self._last_command_processed_at = time.time()
        if self._DEBUG:
            Logger.info("Executing %s at %.5f" % (command, self._last_command_processed_at))

        handler = self._command_mapping[command.__class__](self._container, self._song)
        UndoFacade.begin_undo_step()
        return handler.handle(command)

    def _is_duplicate_command(self, command):
        # type: (SerializableCommand) -> bool
        """
            Sometimes command are duplicated, couldn't find why yet
            Reloading ableton does the trick, it seems that the script is loaded twice
        """
        if self._last_command_processed_at is None \
                or time.time() - self._last_command_processed_at >= 0.02:
            return False

        return type(self._last_command) == type(command)
