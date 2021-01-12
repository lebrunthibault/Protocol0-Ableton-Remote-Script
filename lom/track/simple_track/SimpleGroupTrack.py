from functools import partial

from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class SimpleGroupTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(SimpleGroupTrack, self).__init__(*a, **k)
        self.push2_selected_main_mode = 'mix'

    def _added_track_init(self):
        seq = Sequence()
        seq.add(wait=1)
        self.is_folded = False
        if len(self.devices) == 0:
            seq.add(partial(self.parent.browserManager.load_rack_device, "Mix Base Rack"))

        return seq.done()
