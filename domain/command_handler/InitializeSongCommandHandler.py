from protocol0.domain.command.InitializeSongCommand import InitializeSongCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.SongManager import SongManager
from protocol0.domain.lom.song.SongScenesManager import SongScenesManager
from protocol0.domain.lom.song.SongTracksManager import SongTracksManager


class InitializeSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (InitializeSongCommand) -> None
        self._container.get(SongTracksManager).tracks_listener()
        self._container.get(SongScenesManager).scenes_listener()
        self._container.get(SongManager).init_song()
