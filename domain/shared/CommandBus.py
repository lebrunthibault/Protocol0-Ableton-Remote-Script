from typing import Dict, Type

import protocol0.application.command as command_package
import protocol0.domain.command_handler as command_handler_package
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.domain.shared.CommandBusInterface import CommandBusInterface
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import import_package


class CommandBus(CommandBusInterface):
    _MAPPING = {}

    @classmethod
    def _get_mapping(cls):
        # type: () -> Dict[Type[SerializableCommand], Type[CommandHandlerInterface]]
        if cls._MAPPING:
            return cls._MAPPING

        import_package(command_package)
        import_package(command_handler_package)

        handler_classes = CommandHandlerInterface.__subclasses__()
        command_classes = SerializableCommand.__subclasses__()

        handler_names_to_class = {handler_class.__name__: handler_class for handler_class in handler_classes}

        # matching on class name
        for command_class in command_classes:
            handler_class_name = command_class.__name__ + "Handler"
            if handler_class_name not in handler_names_to_class:
                raise Protocol0Error("Couldn't find matching handler for %s" % command_class)

            cls._MAPPING[command_class] = handler_names_to_class[handler_class_name]

        return cls._MAPPING

    @classmethod
    def execute_from_string(cls, command_string):
        # type: (str) -> None
        command = SerializableCommand.unserialize(command_string)
        cls.dispatch(command)

    @classmethod
    def dispatch(cls, command):
        # type: (SerializableCommand) -> None
        from protocol0.application.Protocol0 import Protocol0

        handler = cls._get_mapping()[command.__class__](Protocol0.CONTAINER)
        handler.handle(command)
