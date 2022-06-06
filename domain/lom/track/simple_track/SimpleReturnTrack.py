from typing import Any

from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class SimpleReturnTrack(SimpleAudioTrack):
    IS_ACTIVE = False

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleReturnTrack, self).__init__(*a, **k)
        self.appearance.disconnect()
