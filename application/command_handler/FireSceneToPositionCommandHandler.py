from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class FireSceneToPositionCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (FireSceneToPositionCommand) -> Sequence
        return SongFacade.last_manually_started_scene().fire_to_position()
