from protocol0.application.command.ScrollScenesCommand import ScrollScenesCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface


class ScrollScenesCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollScenesCommand) -> None
        self._song.scroll_scenes(command.go_next)
