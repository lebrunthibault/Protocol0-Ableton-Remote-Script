from protocol0.application.command.DrumRackToSimplerCommand import DrumRackToSimplerCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DrumRackService import DrumRackService


class DrumRackToSimplerCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (DrumRackToSimplerCommand) -> None
        self._container.get(DrumRackService).drum_rack_to_simpler()
