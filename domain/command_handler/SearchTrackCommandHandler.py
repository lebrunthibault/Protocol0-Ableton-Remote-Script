from protocol0.application.command.SearchTrackCommand import SearchTrackCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface


class SearchTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (SearchTrackCommand) -> None
        self._container.keyword_search_manager.search_track(command.search)
