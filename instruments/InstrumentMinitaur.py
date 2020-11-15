from a_protocol_0.actions.AhkCommands import AhkCommands
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument


class InstrumentMinitaur(AbstractInstrument):
    NUMBER_OF_PRESETS = 9

    def action_show(self):
        # type: () -> None
        AhkCommands.select_first_vst()

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> str
        return self.action_scroll_via_program_change(go_next)
