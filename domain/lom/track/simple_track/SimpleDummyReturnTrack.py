from functools import partial

from typing import Any, cast

from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class SimpleDummyReturnTrack(SimpleDummyTrack):
    TRACK_NAME = "ds"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleDummyReturnTrack, self).__init__(*a, **k)
        self.automation.disable_device()

    @classmethod
    def is_track_valid(cls, track):
        # type: (AbstractTrack) -> bool
        return SimpleDummyTrack.is_track_valid(track) and track.output_routing.type == \
               OutputRoutingTypeEnum.SENDS_ONLY

    def on_added(self):
        # type: () -> None
        super(SimpleDummyReturnTrack, self).on_added()
        self.input_routing.track = cast(SimpleAudioTrack, self.group_track)
        # we need to defer this
        Scheduler.defer(partial(setattr, self.output_routing, "type",
                                OutputRoutingTypeEnum.SENDS_ONLY))
