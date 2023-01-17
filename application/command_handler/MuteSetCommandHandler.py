from protocol0.application.command.MuteSetCommand import MuteSetCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class MuteSetCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (MuteSetCommand) -> None
        Song.master_track().toggle_mute()
