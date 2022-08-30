import time
from functools import partial

from typing import Dict, Type, Optional

import protocol0.application.command as command_package
import protocol0.application.command_handler as command_handler_package
from protocol0.application.CommandBusHistory import CommandBusHistory
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.utils import import_package
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence

CommandMapping = Dict[Type[SerializableCommand], Type[CommandHandlerInterface]]


class CommandBus(object):
    _DEBUG = False
    _INSTANCE = None  # type: Optional[CommandBus]

    def __init__(self, container):
        # type: (ContainerInterface) -> None
        self._container = container
        self._command_mapping = self._create_command_mapping()

        self._history = CommandBusHistory()
        CommandBus._INSTANCE = self

    def _create_command_mapping(self):
        # type: () -> CommandMapping
        import_package(command_package)
        import_package(command_handler_package)

        handler_classes = CommandHandlerInterface.__subclasses__()
        command_classes = SerializableCommand.__subclasses__()

        handler_names_to_class = {
            handler_class.__name__: handler_class for handler_class in handler_classes
        }

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
        if cls._INSTANCE is None:
            return None
        else:
            # call this as a regular method
            return cls._INSTANCE._dispatch_command(command)

    @handle_error
    def _dispatch_command(self, command):
        # type: (SerializableCommand) -> Optional[Sequence]
        start_at = time.time()

        self._history.push(command)

        handler = self._command_mapping[command.__class__](self._container)
        seq = Sequence()
        seq.add(partial(handler.handle, command))

        if self._DEBUG:
            seq.add(partial(Logger.info, "%s : took %.3fs" % (command, time.time() - start_at)))

        return seq.done()

    @classmethod
    def has_recent_command(cls, command_class, delay):
        # type: (Type[SerializableCommand], int) -> bool
        return cls._INSTANCE._history.has_recent_command(command_class, delay)
