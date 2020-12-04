from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentSerum(AbstractInstrument):
    PRESETS_PATH = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"

    def get_display_name(self, preset_name):
        # type: (str) -> str
        return preset_name.replace("User\\", "")
