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
        if self.track.preset_index == -1:
            new_preset_index = 0
        else:
            new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index = new_preset_index % self.NUMBER_OF_PRESETS

        action_list = "; midi pc 1 {0}".format(new_preset_index)
        action_list += "; {0}/name '{1}'".format(self.track.index, self.track.name.get_track_name_for_preset_index(new_preset_index))

        return action_list