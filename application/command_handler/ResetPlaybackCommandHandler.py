from protocol0.application.command.ResetPlaybackCommand import ResetPlaybackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent


class ResetPlaybackCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ResetPlaybackCommand) -> None
        self._container.get(PlaybackComponent).reset()
