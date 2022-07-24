from protocol0.application.command.ResetSongCommand import ResetSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.infra.persistence.SongDataService import SongDataService


class ResetSongCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ResetSongCommand) -> None
        self._container.get(PlaybackComponent).reset()
        self._container.get(SongDataService).save()
