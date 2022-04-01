from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class LoadDeviceCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadDeviceCommand) -> Sequence
        device_enum = DeviceEnum.from_value(command.device_name.upper())  # type: DeviceEnum
        Logger.dev(device_enum)
        return self._container.get(BrowserServiceInterface).load_device_from_enum(device_enum)
