from a_protocol_0.actions.AhkCommands import AhkCommands
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument


class InstrumentProphet(AbstractInstrument):
    def __init__(self, *a, **k):
        super(InstrumentProphet, self).__init__(*a, **k)
        self.needs_activation = True

    def action_show(self):
        # type: () -> None
        self.parent.log_message("show_and_activate_rev2_editor")
        AhkCommands.show_and_activate_rev2_editor()

