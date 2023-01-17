from typing import Optional

from protocol0.application.command.ToggleArmCommand import ToggleArmCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ToggleArmCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ToggleArmCommand) -> Optional[Sequence]
        return Song.current_track().arm_state.toggle()
