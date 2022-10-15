from protocol0.application.command.PlayPauseSongCommand import PlayPauseSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent


class PlayPauseSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (PlayPauseSongCommand) -> None
        return self._container.get(PlaybackComponent).play_pause()
