from protocol0.application.command.ToggleRoomEQCommand import ToggleRoomEQCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ToggleRoomEQCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ToggleRoomEQCommand) -> None
        SongFacade.master_track().toggle_room_eq()
