from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.shared.sequence.Sequence import Sequence


class LoadDeviceCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadDeviceCommand) -> Sequence
        return self._container.get(DeviceService).load_device(command.enum_name)
