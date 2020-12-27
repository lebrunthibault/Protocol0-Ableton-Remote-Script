from os import listdir
from os.path import join
from typing import Optional

from _Framework.Util import find_if
from a_protocol_0.consts import SAMPLE_PATH
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import debounce
from a_protocol_0.utils.utils import scroll_values


class InstrumentSimpler(AbstractInstrument):
    PRESET_EXTENSION = ".wav"

    def __init__(self, *a, **k):
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.can_be_shown = False
        self.activated = True
        self.set_method_property(self.get_presets, "wait_time", 10)

    @property
    def selected_category(self):
        # type: () -> Optional[str]
        """ first checking the name of the track to be able to scroll categories without looking up samples """
        if TrackName(self.track).name in listdir(SAMPLE_PATH):
            return TrackName(self.track).name
        else:
            return find_if(lambda f: self.track.name in f.lower(), listdir(SAMPLE_PATH))

    def _get_presets_path(self):
        # type: () -> str
        if not self.selected_category:
            raise Exception("the track name does not correspond with a sample directory")

        return join(SAMPLE_PATH, self.selected_category)

    @debounce(2)
    def set_preset(self, preset_index):
        # type: (int) -> None
        self.parent.browserManager.load_sample(self.preset_names[preset_index])

    def action_scroll_categories(self, go_next):
        # type: (bool) -> None
        selected_category = scroll_values(listdir(SAMPLE_PATH), self.selected_category, go_next)
        TrackName(self.track).name = selected_category
