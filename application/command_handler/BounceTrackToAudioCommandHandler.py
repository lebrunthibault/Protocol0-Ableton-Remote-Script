from protocol0.application.command.BounceTrackToAudioCommand import BounceTrackToAudioCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackService import \
    MatchingTrackService


class BounceTrackToAudioCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (BounceTrackToAudioCommand) -> None
        self._container.get(MatchingTrackService).bounce_current_track()
