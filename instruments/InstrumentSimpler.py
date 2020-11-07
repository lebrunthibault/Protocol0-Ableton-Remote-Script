from os import listdir
from os.path import isfile, join, isdir

from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument


class InstrumentSimpler(AbstractInstrument):
    SAMPLE_PATH = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported"

    @property
    def action_show(self):
        # type: () -> str
        return ""

    def action_scroll_preset_or_sample(self, go_next):
        # type: (bool) -> str
        sample_path = join(self.SAMPLE_PATH, self.track.name)
        if not isdir(sample_path):
            raise Exception("the track name does not correspond with a sample directory")

        samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]
        current_sample = self.track.devices[0].name + ".wav"

        if current_sample in samples:
            next_sample_index = samples.index(current_sample) + 1 if go_next else samples.index(current_sample) - 1
        else:
            next_sample_index = 0
        next_sample = samples[next_sample_index % len(samples)]

        return "LOADSAMPLE '{0}'".format(next_sample)
