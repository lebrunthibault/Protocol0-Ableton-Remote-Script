from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.Colors import Colors


class InstrumentProphet(AbstractInstrument):
    COLOR = Colors.PROPHET

    def __init__(self, *a, **k):
        super(InstrumentProphet, self).__init__(*a, **k)
        self.needs_activation = True

    def activate(self):
        # type: () -> None
        self.track.is_selected = True
        self.parent.ahk_commands.show_and_activate_rev2_editor()
