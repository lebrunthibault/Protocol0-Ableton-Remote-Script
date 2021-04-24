from functools import partial

from typing import Any, Optional

from a_protocol_0.enums.Push2MainModeEnum import Push2MainModeEnum
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.sequence.Sequence import Sequence


class SimpleGroupTrack(AbstractGroupTrack):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleGroupTrack, self).__init__(*a, **k)
        self.parent.log_dev("%s has sub tracks %s" % (self, self.sub_tracks))

        self._single_sub_track_routing = self._get_single_sub_track_routing()
        # enforce this (e.g. when deleting automation tracks)
        [sub_track.set_output_routing_to(self) for sub_track in self.sub_tracks]

        self.push2_selected_main_mode = Push2MainModeEnum.MIX

    def _added_track_init(self, *a, **k):
        # type: (Any, Any) -> Sequence
        seq = Sequence()
        self.is_folded = False

        self._sync_group_output_routing()
        self.change_appearance_to_sub_tracks_instrument()

        if not self.base_track.has_device("Mix Rack"):
            seq.add(partial(self.load_any_device, DeviceType.RACK_DEVICE, "Mix Rack"))

        for sub_track in self.sub_tracks:
            sub_track._added_track_init(arm=False)

        return seq.done()

    def arm_track(self):
        # type: () -> Optional[Sequence]
        self.is_folded = not self.is_folded
        return None

    def change_appearance_to_sub_tracks_instrument(self):
        # type: () -> None
        instrument_classes = list(
            set([sub_track.instrument.__class__ for sub_track in self.sub_tracks if sub_track.instrument])
        )

        if len(instrument_classes) == 1:
            instrument_class = instrument_classes[0]
            self.track_name.update(base_name=instrument_class.NAME)
            self.color = instrument_class.TRACK_COLOR

    def _get_single_sub_track_routing(self):
        # type: () -> Optional[Any]
        output_routing_objects = list(
            set([sub_track.output_routing_type.attached_object for sub_track in self.sub_tracks])
        )
        if len(output_routing_objects) == 1 and output_routing_objects[0] not in (
            None,
            self,
            self.song.master_track,
        ):
            return output_routing_objects[0]
        else:
            return None

    def _sync_group_output_routing(self):
        # type: () -> None
        """
        if all subtracks (usually only one) are mapped to a single different track (e.g. a bus)
        then route the group track to this track
        Usually happens when grouping a single track routed to an audio bus
        """
        if self._single_sub_track_routing:
            self.set_output_routing_to(self._single_sub_track_routing)

    def record(self, *a, **k):
        # type: (Any, Any) -> None
        pass
