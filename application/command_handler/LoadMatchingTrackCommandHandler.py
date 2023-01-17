from protocol0.application.command.LoadMatchingTrackCommand import LoadMatchingTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.Song import Song

class LoadMatchingTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadMatchingTrackCommand) -> None
        Song.selected_track(SimpleAudioTrack).load_full_track()


