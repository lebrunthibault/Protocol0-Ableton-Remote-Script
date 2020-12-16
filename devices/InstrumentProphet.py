from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentProphet(AbstractInstrument):
    def activate(self):
        # type: () -> None
        self.parent.keyboardShortcutManager.show_and_activate_rev2_editor()
