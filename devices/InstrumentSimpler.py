from os import listdir
from os.path import join

from _Framework.Util import find_if
from a_protocol_0.consts import SAMPLE_PATH
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.utils.decorators import debounce


class InstrumentSimpler(AbstractInstrument):
    PRESET_EXTENSION = ".wav"

    def __init__(self, *a, **k):
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.can_be_shown = False
        self.activated = True
        dir_name = find_if(lambda f: self.track.name in f.lower(), listdir(SAMPLE_PATH))
        if not dir_name:
            raise Exception("the track name does not correspond with a sample directory")

        self.PRESETS_PATH = join(SAMPLE_PATH, dir_name)

    @debounce
    def _set_preset(self, preset_index, _):
        # type: (int, bool) -> None
        self.parent.clyphxBrowserManager.load_sample(None, "'%s'" % self.preset_names[preset_index])
