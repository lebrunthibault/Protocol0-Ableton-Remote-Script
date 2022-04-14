from protocol0.application.command.SelectOrLoadDeviceCommand import SelectOrLoadDeviceCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.shared.sequence.Sequence import Sequence


class SelectOrLoadDeviceCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (SelectOrLoadDeviceCommand) -> Sequence
        return self._container.get(DeviceService).show_or_load_device(command.device_name)
