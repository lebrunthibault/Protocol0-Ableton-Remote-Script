from protocol0.application.command.LoadDrumTrackCommand import LoadDrumTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class LoadDrumTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadDrumTrackCommand) -> Sequence
        return SongFacade.drums_track().add_track(command.drum_name)
