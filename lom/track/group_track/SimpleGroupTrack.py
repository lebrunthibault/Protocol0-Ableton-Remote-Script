from functools import partial

from typing import Any, Optional

from a_protocol_0.enums.Push2MainModeEnum import Push2MainModeEnum
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class SimpleGroupTrack(AbstractGroupTrack):
    DEFAULT_NAME = "Group"

    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(SimpleGroupTrack, self).__init__(base_group_track=base_group_track, *a, **k)
        self._single_sub_track_routing = self._get_single_sub_track_routing()
        # [sub_track.set_output_routing_to(self) for sub_track in self.sub_tracks]

        self.push2_selected_main_mode = Push2MainModeEnum.MIX.value

    def _added_track_init(self, *a, **k):
        # type: (Any, Any) -> Sequence
        seq = Sequence()
        self.is_folded = False

        # self._sync_group_output_routing()

        if not self.base_track.has_device("Mix Rack"):
            seq.add(partial(self.load_any_device, DeviceType.RACK_DEVICE, "Mix Rack"))

        return seq.done()

    def arm_track(self):
        # type: () -> Optional[Sequence]
        self.is_folded = not self.is_folded
        if not self.is_folded:
            self.sub_tracks[0].select()
        return None

    def _get_single_sub_track_routing(self):
        # type: () -> Optional[Any]
        output_routing_objects = list(
            set([sub_track.output_routing_type.attached_object for sub_track in self.sub_tracks])
        )
        if len(output_routing_objects) == 1 and output_routing_objects[0] not in (
            None,
            self._track,
            self.song.master_track._track,
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

    @property
    def computed_base_name(self):
        # type: () -> str
        # checking if all sub tracks have the same instrument
        sub_tracks_instruments = [sub_track.instrument for sub_track in self.sub_tracks if sub_track.instrument]
        sub_tracks_instrument_classes = [instrument.__class__ for instrument in sub_tracks_instruments]
        if len(sub_tracks_instruments) == len(self.sub_tracks) and len(set(sub_tracks_instrument_classes)) == 1:
            return self.sub_tracks[0].instrument.NAME

        # checking if all sub tracks have the same prefix
        sub_tracks_name_prefixes = [sub_track.name_prefix for sub_track in self.sub_tracks]
        if len(sub_tracks_name_prefixes) == 1 and sub_tracks_name_prefixes[0]:
            return sub_tracks_name_prefixes[0]
        else:
            return self.DEFAULT_NAME

    @property
    def computed_color(self):
        # type: () -> int
        sub_track_colors = [sub_track.color for sub_track in self.sub_tracks]
        if len(set(sub_track_colors)) == 1:
            return sub_track_colors[0]
        else:
            return self.DEFAULT_COLOR.value
