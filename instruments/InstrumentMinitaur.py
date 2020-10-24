from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentMinitaur(AbstractInstrument):
    NUMBER_OF_PRESETS = 9

    @property
    def action_show(self):
        # type: () -> str
        return BomeCommands.SELECT_FIRST_VST

    def action_scroll_preset_or_sample(self, go_next):
        # type: (bool) -> str
        return self.action_scroll_via_program_change(go_next)