from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentNull(AbstractInstrument):
    def __init__(self, *a, **k):
        super(InstrumentNull, self).__init__(*a, **k)
        self.is_null = True
        self.can_be_shown = False
