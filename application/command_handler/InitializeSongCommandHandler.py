from protocol0.application.command.InitializeSongCommand import InitializeSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.song.SongService import SongService
from protocol0.domain.lom.track.TrackService import TrackService


class InitializeSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (InitializeSongCommand) -> None
        self._container.get(TrackService).tracks_listener()
        self._container.get(SceneService).scenes_listener()
        self._container.get(SongService).init_song()
