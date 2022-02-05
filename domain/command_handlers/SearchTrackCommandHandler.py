from protocol0.application.system_command.SearchTrackCommand import SearchTrackCommand
from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface


class SearchTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (SearchTrackCommand) -> None
        from protocol0 import Protocol0

        Protocol0.SELF.keywordSearchManager.search_track(command.search)
