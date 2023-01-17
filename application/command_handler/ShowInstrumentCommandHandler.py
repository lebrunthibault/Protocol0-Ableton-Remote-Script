from protocol0.application.command.ShowInstrumentCommand import ShowInstrumentCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.shared.Song import Song


class ShowInstrumentCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ShowInstrumentCommand) -> None
        self._container.get(InstrumentDisplayService).show_instrument(Song.current_track())
