from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentMinitaur(AbstractInstrument):
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"

    def activate(self):
        # type: () -> None
        self.parent.keyboardShortcutManager.toggle_minitaur_editor()
