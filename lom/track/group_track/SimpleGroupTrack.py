from functools import partial

from typing import Any, Optional, Type

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.devices.InstrumentSimpler import InstrumentSimpler
from protocol0.enums.Push2MainModeEnum import Push2MainModeEnum
from protocol0.lom.device.DeviceType import DeviceType
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import find_if


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

    @property
    def instrument_class(self):
        # type: () -> Optional[Type[AbstractInstrument]]
        sub_tracks_instruments = [sub_track.instrument for sub_track in self.sub_tracks if sub_track.instrument]
        sub_tracks_instrument_classes = list(set([instrument.__class__ for instrument in sub_tracks_instruments]))
        if len(sub_tracks_instruments) == len(self.sub_tracks) and len(sub_tracks_instrument_classes) == 1:
            return sub_tracks_instrument_classes[0]
        else:
            return None

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

    def session_record(self, *a, **k):
        # type: (Any, Any) -> None
        pass

    @property
    def computed_base_name(self):
        # type: () -> str
        common_subtracks_instrument_class = self._common_subtracks_instrument_class
        if common_subtracks_instrument_class == InstrumentSimpler and \
                find_if(lambda t: "kick" in t.name.lower(), self.sub_tracks):
            return "Drums"

        if common_subtracks_instrument_class:
            return common_subtracks_instrument_class.NAME

        def _name_prefix(track):
            # type: (AbstractTrack) -> str
            return track.base_track.track_name.base_name.split(" ")[0]

        # checking if all sub tracks have the same prefix
        unique_sub_tracks_name_prefixes = list(set([_name_prefix(sub_track) for sub_track in self.sub_tracks]))
        if len(unique_sub_tracks_name_prefixes) == 1 and unique_sub_tracks_name_prefixes[0]:
            return unique_sub_tracks_name_prefixes[0]

        return self.DEFAULT_NAME

    @property
    def _common_subtracks_instrument_class(self):
        # type: () -> Optional[Type[AbstractInstrument]]
        sub_tracks_instrument_classes = filter(None, [sub_track.instrument_class for sub_track in self.sub_tracks])

        unique_sub_tracks_instrument_classes = list(set(sub_tracks_instrument_classes))
        if len(sub_tracks_instrument_classes) == len(self.sub_tracks) and len(
                unique_sub_tracks_instrument_classes) == 1:
            return unique_sub_tracks_instrument_classes[0]
        else:
            return None

    @property
    def computed_color(self):
        # type: () -> int
        sub_track_colors = [sub_track.color for sub_track in self.sub_tracks]
        if len(set(sub_track_colors)) == 1:
            return sub_track_colors[0]
        else:
            return self.DEFAULT_COLOR.value
