from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentProphet(AbstractInstrument):
    @property
    def show_command(self):
        return BomeCommands.SHOW_AND_ACTIVATE_REV2_EDITOR
