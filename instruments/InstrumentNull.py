from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument


class InstrumentNull(AbstractInstrument):
    def __init__(self, simple_track):
        # type: ("SimpleTrack") -> None
        super(InstrumentNull, self).__init__(simple_track)
        self.is_null = False

    def action_show(self):
        # type: () -> None
        return

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> str
        pass
