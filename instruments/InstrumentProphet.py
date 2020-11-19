from a_protocol_0.actions.AhkCommands import AhkCommands
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument


class InstrumentProphet(AbstractInstrument):
    NUMBER_OF_PRESETS = 128

    def action_show(self):
        # type: () -> None
        self.parent.log_message("show_and_activate_rev2_editor")
        AhkCommands.show_and_activate_rev2_editor()

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> str
        return self.action_scroll_via_program_change(go_next)
