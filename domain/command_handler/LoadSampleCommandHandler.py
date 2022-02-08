from protocol0.domain.command.LoadSampleCommand import LoadSampleCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface


class LoadSampleCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadSampleCommand) -> None
        self._container.get(BrowserServiceInterface).load_sample(command.sample_name)
