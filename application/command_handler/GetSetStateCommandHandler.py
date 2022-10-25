from protocol0.application.command.GetSetStateCommand import GetSetStateCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.AbletonSet import AbletonSet


class GetSetStateCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (GetSetStateCommand) -> None
        self._container.get(AbletonSet).notify(force=True)
