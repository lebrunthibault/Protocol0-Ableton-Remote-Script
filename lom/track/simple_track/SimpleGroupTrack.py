from collections import defaultdict
from functools import partial

from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class SimpleGroupTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(SimpleGroupTrack, self).__init__(*a, **k)
        self.push2_selected_main_mode = 'mix'

    def _added_track_init(self):
        seq = Sequence()
        self.is_folded = False
        self.parent.log_debug(self.sub_tracks[0].output_routing_type.attached_object)
        self.parent.log_debug(self.sub_tracks[0].output_routing_type.display_name)
        output_routing_tracks = list(set([sub_track.output_routing_type.attached_object for sub_track in self.sub_tracks]))
        if len(output_routing_tracks) == 1 and output_routing_tracks[0] and output_routing_tracks[0] != self.song.master_track:
            self.attach_output_routing_to(output_routing_tracks[0])
            [sub_track.attach_output_routing_to(self) for sub_track in self.sub_tracks]

        if len(self.devices) == 0:
            seq.add(partial(self.parent.browserManager.load_rack_device, "Mix Base Rack"))

        return seq.done()
