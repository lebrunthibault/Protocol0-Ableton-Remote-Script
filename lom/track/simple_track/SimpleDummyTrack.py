from functools import partial

from typing import Any, Optional, TYPE_CHECKING

import Live
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.DeviceParameterEnum import DeviceParameterEnum
from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class SimpleDummyTrack(SimpleAudioTrack):
    KEEP_CLIPS_ON_ADDED = True

    def __init__(self, track, *a, **k):
        # type: (Live.Track.Track, Any, Any) -> None
        super(SimpleDummyTrack, self).__init__(track=track, *a, **k)

        self.abstract_group_track = None  # type: Optional[ExternalSynthTrack]

    def post_init(self):
        # type: () -> None
        super(SimpleDummyTrack, self).post_init()
        self.parent.defer(self._rename_track)

    def _added_track_init(self):
        # type: () -> Sequence
        self.has_monitor_in = True
        self.input_routing_type = InputRoutingTypeEnum.NO_INPUT
        seq = Sequence()
        seq.add(super(SimpleDummyTrack, self)._added_track_init)
        seq.add(self._insert_dummy_rack)
        seq.add(self._insert_dummy_clip)

        return seq.done()

    def _insert_dummy_rack(self):
        # type: () -> Optional[Sequence]
        if not self.load_device_from_enum(DeviceEnum.DUMMY_RACK):
            return self.parent.browserManager.load_device_from_enum(DeviceEnum.DUMMY_RACK)
        else:
            return None

    def _insert_dummy_clip(self):
        # type: () -> Optional[Sequence]
        if not self.song.template_dummy_clip or len(self.clips):
            return None

        cs = self.clip_slots[self.song.selected_scene.index]
        seq = Sequence()
        seq.add(partial(self.song.template_dummy_clip.clip_slot.duplicate_clip_to, cs))
        seq.add(self._create_dummy_automation)
        return seq.done()

    def _create_dummy_automation(self):
        # type: () -> None
        clip = self.clip_slots[self.song.selected_scene.index].clip
        dummy_rack = self.get_device_from_enum(DeviceEnum.DUMMY_RACK)
        dummy_rack_gain = dummy_rack.get_parameter_by_name(DeviceParameterEnum.DUMMY_RACK_GAIN)
        envelope = clip.create_automation_envelope(parameter=dummy_rack_gain)
        # envelope.insert_step(0, 0, 1)
        envelope.insert_step(clip.loop_end, 0, 1)
        clip.show_envelope_parameter(dummy_rack_gain)
        clip.play()

    def _rename_track(self):
        # type: () -> None
        self.name = "dummy %d" % (self.abstract_group_track.dummy_tracks.index(self) + 1)
