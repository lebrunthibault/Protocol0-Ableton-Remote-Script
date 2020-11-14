from ClyphX_Pro.clyphx_pro.user_actions.actions.AhkCommands import AhkCommands
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentMinitaur(AbstractInstrument):
    NUMBER_OF_PRESETS = 9

    def action_show(self):
        # type: () -> None
        AhkCommands.select_first_vst()

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> str
        return self.action_scroll_via_program_change(go_next)
