from ableton.v2.control_surface.mode import Mode, ModesComponent
from protocol0.domain.lom.instrument.InstrumentSelectedEvent import InstrumentSelectedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class P0ShowInstrumentMode(Mode):
    def __init__(self, main_modes):
        # type: (ModesComponent) -> None
        self._main_modes = main_modes

    def enter_mode(self):
        # type: () -> None
        """cancel mode switch and dispatch event"""
        previous_mode = self._main_modes._mode_stack.clients[0]
        self._main_modes.selected_mode = previous_mode

        DomainEventBus.emit(InstrumentSelectedEvent())
