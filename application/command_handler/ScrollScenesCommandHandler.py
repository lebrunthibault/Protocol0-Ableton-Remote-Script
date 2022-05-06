from protocol0.application.command.ScrollScenesCommand import ScrollScenesCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent


class ScrollScenesCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollScenesCommand) -> None
        self._container.get(SceneComponent).scroll_scenes(command.go_next)
