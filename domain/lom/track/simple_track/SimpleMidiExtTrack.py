from typing import Any

from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack


class SimpleMidiExtTrack(SimpleMidiTrack):
    """Tagging class for the main midi track of an ExternalSynthTrack"""

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiExtTrack, self).__init__(*a, **k)
        self.clip_tail.active = False
