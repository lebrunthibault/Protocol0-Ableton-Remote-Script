from protocol0.application.command.LoadMinitaurCommand import LoadMinitaurCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur


class LoadMinitaurCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadMinitaurCommand) -> None
        InstrumentMinitaur.load_instrument_track()
