from functools import partial

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.sequence.Sequence import Sequence


class SimpleGroupTrack(AbstractGroupTrack):
    def __init__(self, *a, **k):
        super(SimpleGroupTrack, self).__init__(*a, **k)
        [setattr(sub_track, "abstract_group_track", self) for sub_track in self.sub_tracks]

        self.track_name.display_playing_slot_index = False

        self._single_sub_track_routing = self._get_single_sub_track_routing()
        # enforce this (e.g. when deleting automation tracks)
        [sub_track.set_output_routing_to(self) for sub_track in self.sub_tracks]

        self.push2_selected_main_mode = 'mix'
        self.can_be_armed = False
        self.selection_tracks = [self.base_track]  # sub tracks are independent

    def _added_track_init(self):
        seq = Sequence()
        self.is_folded = False

        self._sync_group_output_routing()
        self._rename_to_sub_tracks_instrument()

        if not self.has_device("Mix Rack"):
            seq.add(partial(self.load_any_device, DeviceType.RACK_DEVICE, "Mix Rack"))

        return seq.done()

    def action_arm_track(self):
        self.is_folded = not self.is_folded

    def _rename_to_sub_tracks_instrument(self):
        instrument_classes = list(set([sub_track.instrument.__class__ for sub_track in self.sub_tracks]))
        if len(instrument_classes) == 1:
            instrument_class = instrument_classes[0]  # type: AbstractInstrument
            self.track_name.set_track_name(base_name=instrument_class.NAME)

    def _get_single_sub_track_routing(self):
        output_routing_objects = list(
            set([sub_track.output_routing_type.attached_object for sub_track in self.sub_tracks]))
        if len(output_routing_objects) == 1 and output_routing_objects[0] not in (None, self, self.song.master_track):
            return output_routing_objects[0]

    def _sync_group_output_routing(self):
        """
            if all subtracks (usually only one) are mapped to a single different track (e.g. a bus)
            then route the group track to this track
            Usually happens when grouping a single track routed to an audio bus
        """
        if self._single_sub_track_routing:
            self.set_output_routing_to(self._single_sub_track_routing)

    def action_restart_and_record(self, *a, **k):
        pass
