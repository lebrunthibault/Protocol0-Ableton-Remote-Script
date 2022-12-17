from protocol0.application.command.BounceTrackToAudioCommand import BounceTrackToAudioCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.shared.SongFacade import SongFacade


class BounceTrackToAudioCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (BounceTrackToAudioCommand) -> None
        SongFacade.current_external_synth_track().matching_track.copy_from_base_track(
            self._container.get(TrackCrudComponent)
        )
