from typing import Dict, Type

from protocol0.application.system_command.ResetSongCommand import ResetSongCommand
from protocol0.application.system_command.ShowMessageCommand import ShowMessageCommand
from protocol0.domain.CommandBusInterface import CommandBusInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.application.system_command.SerializableCommand import SerializableCommand


class CommandBus(CommandBusInterface):
    from protocol0.application.system_command.ClearLogsCommand import ClearLogsCommand
    from protocol0.application.system_command.ExecuteVocalCommandCommand import ExecuteVocalCommandCommand
    from protocol0.application.system_command.PingCommand import PingCommand
    from protocol0.application.system_command.ProcessSystemResponseCommand import ProcessSystemResponseCommand
    from protocol0.application.system_command.SearchTrackCommand import SearchTrackCommand
    from protocol0.domain.command_handlers.ClearLogsCommandHandler import ClearLogsCommandHandler
    from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface
    from protocol0.domain.command_handlers.ExecuteVocalCommandCommandHandler import ExecuteVocalCommandCommandHandler
    from protocol0.domain.command_handlers.PingCommandHandler import PingCommandHandler
    from protocol0.domain.command_handlers.ProcessSystemResponseCommandHandler import \
        ProcessSystemResponseCommandHandler
    from protocol0.domain.command_handlers.ResetSongCommandHandler import ResetSongCommandHandler
    from protocol0.domain.command_handlers.SearchTrackCommandHandler import SearchTrackCommandHandler
    from protocol0.domain.command_handlers.ShowMessageCommandHandler import ShowMessageCommandHandler

    _MAPPING = {
        ClearLogsCommand: ClearLogsCommandHandler,
        ExecuteVocalCommandCommand: ExecuteVocalCommandCommandHandler,
        PingCommand: PingCommandHandler,
        ProcessSystemResponseCommand: ProcessSystemResponseCommandHandler,
        ResetSongCommand: ResetSongCommandHandler,
        SearchTrackCommand: SearchTrackCommandHandler,
        ShowMessageCommand: ShowMessageCommandHandler
    }  # type: Dict[Type[SerializableCommand], Type[CommandHandlerInterface]]

    @classmethod
    def execute_from_string(cls, command_string):
        # type: (str) -> None
        command = SerializableCommand.unserialize(command_string)
        cls.dispatch(command)

    @classmethod
    def dispatch(cls, command):
        # type: (SerializableCommand) -> None
        if command.__class__ not in cls._MAPPING:
            raise Protocol0Error("%s is not mapped to a command handler")

        handler = cls._MAPPING[command.__class__]()
        handler.handle(command)
