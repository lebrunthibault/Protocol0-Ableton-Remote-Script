from protocol0.application.command.ToggleArmCommand import ToggleArmCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ToggleArmCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ToggleArmCommand) -> None
        SongFacade.current_track().toggle_arm()
