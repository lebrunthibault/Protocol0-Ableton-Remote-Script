from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentNull(AbstractInstrument):
    @property
    def show_command(self):
        return ""
