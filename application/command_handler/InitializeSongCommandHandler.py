from protocol0.application.command.InitializeSongCommand import InitializeSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.song.SongInitService import SongInitService
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.shared.logging.Logger import Logger


class InitializeSongCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (InitializeSongCommand) -> None
        Logger.clear()
        self._container.get(TrackMapperService).tracks_listener()
        self._container.get(SceneService).scenes_listener()
        self._container.get(SongInitService).init_song()
