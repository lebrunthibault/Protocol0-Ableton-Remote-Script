import time
from functools import partial

from _Framework.ControlSurface import get_control_surfaces
from typing import Dict, Type, Optional

import protocol0.application.command as command_package
import protocol0.application.command_handler as command_handler_package
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.command.ScrollScenePositionCommand import ScrollScenePositionCommand
from protocol0.application.command.ScrollSceneTracksCommand import ScrollSceneTracksCommand
from protocol0.application.command.ScrollScenesCommand import ScrollScenesCommand
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.utils import import_package
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence

CommandMapping = Dict[Type[SerializableCommand], Type[CommandHandlerInterface]]


class CommandBus(object):
    _DEBUG = False
    _INSTANCE = None  # type: Optional[CommandBus]
    _DUPLICATE_COMMAND_WHITELIST = (
        ScrollScenePositionCommand,
        ScrollScenesCommand,
        ScrollSceneTracksCommand,
    )
    _DUPLICATE_COMMAND_WARNING_COUNT = 10

    def __init__(self, container):
        # type: (ContainerInterface) -> None
        self._container = container
        self._command_mapping = self._create_command_mapping()
        self._last_command = None  # type: Optional[SerializableCommand]
        self._last_command_processed_at = None  # type: Optional[float]
        self._duplicate_command_count = 0
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
            return cls._INSTANCE._dispatch_command(command)

    @handle_error
    def _dispatch_command(self, command):
        # type: (SerializableCommand) -> Optional[Sequence]
        start_at = time.time()

        if self._is_duplicate_command(command):
            self._duplicate_command_count += 1
            Logger.warning("skipping duplicate command %s: please reload the set" % command)

            from protocol0.application.Protocol0 import Protocol0

            p0_instances = filter(lambda cs: isinstance(cs, Protocol0), get_control_surfaces())
            Logger.warning("number of p0 instances loaded : %s" % len(p0_instances))

            if self._duplicate_command_count == self._DUPLICATE_COMMAND_WARNING_COUNT:
                Backend.client().show_warning(
                    "Reached 10 duplicate commands. Set might need to be reloaded."
                )
            return None

        self._last_command = command
        self._last_command_processed_at = start_at

        handler = self._command_mapping[command.__class__](self._container)
        UndoFacade.begin_undo_step()
        seq = Sequence()
        seq.add(partial(handler.handle, command))
        seq.add(UndoFacade.end_undo_step)

        if self._DEBUG:
            seq.add(partial(Logger.info, "%s : took %.3fs" % (command, time.time() - start_at)))

        return seq.done()

    def _is_duplicate_command(self, command):
        # type: (SerializableCommand) -> bool
        """
        Sometimes command are duplicated, couldn't find why yet
        it seems either that :
        - the midi server is sending duplicate sysex messages (but they are logged only once)
        - the messages are getting duplicated in the midi chain (mido or the loopback midi
        port ..)
        Reloading ableton fixes it

        We mitigate it by forbidding duplicate messages in a certain delay
        """
        return (
            type(command) not in self._DUPLICATE_COMMAND_WHITELIST
            and type(self._last_command) is type(command)
            and self._last_command_processed_at is not None
            and time.time() - self._last_command_processed_at < 0.100
        )
