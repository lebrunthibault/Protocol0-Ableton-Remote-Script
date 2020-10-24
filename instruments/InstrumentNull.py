from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentNull(AbstractInstrument):
    def __init__(self, simple_track):
        # type: ("SimpleTrack") -> None
        super(InstrumentNull, self).__init__(simple_track)
        self.is_null = False

    @property
    def action_show(self):
        # type: () -> str
        return ""

    def action_scroll_preset_or_sample(self, go_next):
        # type: (bool) -> str
        pass
