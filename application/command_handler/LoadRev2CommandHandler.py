from protocol0.application.command.LoadRev2Command import LoadRev2Command
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.instrument.InstrumentInterface import load_instrument_track
from protocol0.domain.lom.instrument.instrument.InstrumentRev2 import InstrumentRev2


class LoadRev2CommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadRev2Command) -> None
        load_instrument_track(InstrumentRev2)

