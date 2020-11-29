from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument


class InstrumentProphet(AbstractInstrument):
    def __init__(self, *a, **k):
        super(InstrumentProphet, self).__init__(*a, **k)
        self.needs_activation = True

    def activate(self):
        # type: () -> None
        self.parent.ahk_commands.show_and_activate_rev2_editor()
