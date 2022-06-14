from typing import Any

from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack


class SimpleDummyReturnTrack(SimpleDummyTrack):
    TRACK_NAME = "ds"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleDummyTrack, self).__init__(*a, **k)
        self.automation.disable_device()

    def on_added(self):
        # type: () -> None
        self.output_routing.type = OutputRoutingTypeEnum.SENDS_ONLY
        super(SimpleDummyReturnTrack, self).on_added()
