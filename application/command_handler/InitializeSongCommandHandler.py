from protocol0.application.command.InitializeSongCommand import InitializeSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.song.SongInitService import SongInitService
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService


class InitializeSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (InitializeSongCommand) -> None
        self._container.get(TrackMapperService).tracks_listener()
        self._container.get(SceneService).scenes_listener()
        self._container.get(SongInitService).init_song()
