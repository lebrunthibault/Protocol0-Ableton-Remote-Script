from protocol0.application.command.InitializeSongCommand import InitializeSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.ScenesService import SongScenesService
from protocol0.domain.lom.song.SongService import SongService
from protocol0.domain.lom.track.TracksService import SongTracksService


class InitializeSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (InitializeSongCommand) -> None
        self._container.get(SongTracksService).tracks_listener()
        self._container.get(SongScenesService).scenes_listener()
        self._container.get(SongService).init_song()
