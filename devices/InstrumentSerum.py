from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentSerum(AbstractInstrument):
    PRESETS_FILE = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"

    def __init__(self, *a, **k):
        super(InstrumentSerum, self).__init__(*a, **k)
        self.NUMBER_OF_PRESETS = len(open(self.PRESETS_FILE).readlines())
        self.has_rack = True
