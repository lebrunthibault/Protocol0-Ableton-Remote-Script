from protocol0.application.command.BounceTrackToAudioCommand import BounceTrackToAudioCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.shared.SongFacade import SongFacade


class BounceTrackToAudioCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (BounceTrackToAudioCommand) -> None
        current_track = SongFacade.current_track()
        assert isinstance(current_track, (ExternalSynthTrack, SimpleMidiTrack)), "Can only bounce midi and ext tracks"

        current_track.matching_track.bounce(
            self._container.get(TrackCrudComponent)
        )
