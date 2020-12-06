from os import listdir
from os.path import isfile, join, isdir

from a_protocol_0.consts import SAMPLE_PATH
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.track.TrackName import TrackName


class InstrumentSimpler(AbstractInstrument):
    def __init__(self, *a, **k):
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.can_be_shown = False
        self._device = None

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        track_name = TrackName(self.track).name
        sample_path = join(SAMPLE_PATH, track_name[0].upper() + track_name[1:])
        if not isdir(sample_path):
            raise Exception("the track name does not correspond with a sample directory")

        samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]
        # instead of self._device because simpler gets new device each time
        current_sample = self.track.selected_device.name + ".wav"

        if current_sample in samples:
            next_sample_index = samples.index(current_sample) + 1 if go_next else samples.index(current_sample) - 1
        else:
            next_sample_index = 0
        next_sample = samples[next_sample_index % len(samples)]

        self.parent.browserManager.load_sample(None, "'%s'" % next_sample)
