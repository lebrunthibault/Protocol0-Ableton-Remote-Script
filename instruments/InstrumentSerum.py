from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument


class InstrumentSerum(AbstractInstrument):
    PRESETS_FILE = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"

    def __init__(self, *a, **k):
        self.NUMBER_OF_PRESETS = len(open(self.PRESETS_FILE).readlines())
        super(InstrumentSerum, self).__init__(*a, **k)

    # def set_preset(self, _, go_next):
    #     # type: (bool, bool) -> None
    #     self.parent.midi.send_control_change_absolute(55 if go_next else 54)
