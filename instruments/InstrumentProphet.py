from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentProphet(AbstractInstrument):
    NUMBER_OF_PRESETS = 128

    def action_show(self):
        # type: () -> None
        BomeCommands.show_and_activate_rev2_editor()

    def action_browse_presets_or_samples(self, go_next):
        # type: (bool) -> str
        return self.action_scroll_via_program_change(go_next)
