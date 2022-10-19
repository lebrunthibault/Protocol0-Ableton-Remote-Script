from protocol0.application.command.MuteSetCommand import MuteSetCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class MuteSetCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (MuteSetCommand) -> None
        SongFacade.master_track().toggle_mute()
