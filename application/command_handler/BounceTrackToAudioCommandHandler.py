from protocol0.application.command.BounceTrackToAudioCommand import BounceTrackToAudioCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.shared.Song import Song


class BounceTrackToAudioCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (BounceTrackToAudioCommand) -> None
        current_track = Song.current_track()
        assert isinstance(current_track, (ExternalSynthTrack, SimpleMidiTrack)), "Can only bounce midi and ext tracks"

        current_track.matching_track.bounce(
            self._container.get(TrackCrudComponent)
        )
