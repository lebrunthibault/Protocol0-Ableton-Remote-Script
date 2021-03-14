import os
from os import listdir
from os.path import join

from _Framework.Util import find_if
from typing import Optional

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.utils.decorators import debounce
from a_protocol_0.utils.utils import scroll_values


class InstrumentSimpler(AbstractInstrument):
    NAME = "Simpler"
    TRACK_COLOR = Colors.SIMPLER
    PRESET_EXTENSION = ".wav"
    SAMPLE_PATH = os.getenv("SAMPLE_PATH")

    def __init__(self, *a, **k):
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.can_be_shown = False
        self.activated = True
        self.set_method_property(self.get_presets, "wait_time", 10)

    @property
    def selected_category(self):
        # type: () -> Optional[str]
        """ first checking the name of the track to be able to scroll categories without looking up samples """
        return find_if(lambda f: self.track.base_name.lower() in f.lower(), listdir(self.SAMPLE_PATH))

    def _get_presets_path(self):
        # type: () -> str
        if not self.selected_category:
            return

        return join(self.SAMPLE_PATH, self.selected_category)

    @debounce(2)
    def set_preset(self, preset_index):
        # type: (int) -> None
        self.parent.browserManager.load_sample(self.preset_names[preset_index])
        self.parent._wait(4, self.track._devices_listener)

    def action_scroll_categories(self, go_next):
        # type: (bool) -> None
        selected_category = scroll_values(listdir(self.SAMPLE_PATH), self.selected_category, go_next)
        self.track.track_name.set(base_name=selected_category)
