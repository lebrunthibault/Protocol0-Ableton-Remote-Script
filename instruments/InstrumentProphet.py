from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentProphet(AbstractInstrument):
    NUMBER_OF_PRESETS = 128

    @property
    def action_show(self):
        # type: () -> str
        return BomeCommands.SHOW_AND_ACTIVATE_REV2_EDITOR

    def action_scroll_preset_or_sample(self, go_next):
        # type: (bool) -> str
        return self.action_scroll_via_program_change(go_next)
