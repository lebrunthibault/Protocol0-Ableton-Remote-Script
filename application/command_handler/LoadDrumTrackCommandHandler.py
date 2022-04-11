from protocol0.application.command.LoadDrumTrackCommand import LoadDrumTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.shared.sequence.Sequence import Sequence


class LoadDrumTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadDrumTrackCommand) -> Sequence
        return self._container.get(TrackFactory).add_drum_track(command.drum_name)
