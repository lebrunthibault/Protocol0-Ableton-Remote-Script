from os import listdir
from os.path import isfile, join, isdir

from a_protocol_0.consts import SAMPLE_PATH
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentSimpler(AbstractInstrument):
    def __init__(self, *a, **k):
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.can_be_shown = False

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        sample_path = join(SAMPLE_PATH, self.track.base_name)
        if not isdir(sample_path):
            raise Exception("the track name does not correspond with a sample directory")

        samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]
        current_sample = self.track.devices[0].name + ".wav"

        if current_sample in samples:
            next_sample_index = samples.index(current_sample) + 1 if go_next else samples.index(current_sample) - 1
        else:
            next_sample_index = 0
        next_sample = samples[next_sample_index % len(samples)]

        self._do_load_item(self._get_item_for_category('samples', next_sample), 'Sample')
