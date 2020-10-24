from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentMinitaur(AbstractInstrument):
    @property
    def action_show(self):
        # type: () -> str
        return BomeCommands.SELECT_FIRST_VST

    def action_scroll_preset_or_sample(self, go_next):
        # type: (bool) -> str
        pass
