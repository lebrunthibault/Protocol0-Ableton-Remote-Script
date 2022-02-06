from typing import Dict, Type

from protocol0.application.command.ResetSongCommand import ResetSongCommand
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.application.command.ShowMessageCommand import ShowMessageCommand
from protocol0.domain.CommandBusInterface import CommandBusInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class CommandBus(CommandBusInterface):
    from protocol0.application.command.ClearLogsCommand import ClearLogsCommand
    from protocol0.application.command.ExecuteVocalCommandCommand import ExecuteVocalCommandCommand
    from protocol0.application.command.PingCommand import PingCommand
    from protocol0.application.command.ProcessSystemResponseCommand import ProcessSystemResponseCommand
    from protocol0.application.command.SearchTrackCommand import SearchTrackCommand
    from protocol0.domain.command_handler.ClearLogsCommandHandler import ClearLogsCommandHandler
    from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
    from protocol0.domain.command_handler.ExecuteVocalCommandCommandHandler import ExecuteVocalCommandCommandHandler
    from protocol0.domain.command_handler.PingCommandHandler import PingCommandHandler
    from protocol0.domain.command_handler.ProcessSystemResponseCommandHandler import \
        ProcessSystemResponseCommandHandler
    from protocol0.domain.command_handler.ResetSongCommandHandler import ResetSongCommandHandler
    from protocol0.domain.command_handler.SearchTrackCommandHandler import SearchTrackCommandHandler
    from protocol0.domain.command_handler.ShowMessageCommandHandler import ShowMessageCommandHandler

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

    # def _get_mapping(self):
    #     # type: () -> Dict[Type[SerializableCommand], Type[CommandHandlerInterface]]
    #     if self._MAPPING:
    #         return self._MAPPING
    #
    #     # noinspection PyUnusedLocal
    #     handlers_files = listdir(Config.ROOT_DIR + "\\domain\\command_handler")
    #
    #     return {}

    @classmethod
    def dispatch(cls, command):
        # type: (SerializableCommand) -> None
        if command.__class__ not in cls._MAPPING:
            raise Protocol0Error("%s is not mapped to a command handler")

        from protocol0 import Protocol0
        handler = cls._MAPPING[command.__class__](Protocol0.CONTAINER)
        handler.handle(command)
