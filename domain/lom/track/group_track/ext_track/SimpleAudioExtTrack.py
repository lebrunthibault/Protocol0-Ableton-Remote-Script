from typing import Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
        ExternalSynthTrack,
    )
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class SimpleAudioExtTrack(SimpleAudioTrack):
    """Tagging class for the main audio track of and ExternalSynthTrack"""

    def __init__(self, *a, **k):
        # type:(Any, Any) -> None
        super(SimpleAudioExtTrack, self).__init__(*a, **k)
        self.abstract_group_track = None  # type: Optional[ExternalSynthTrack]
        self.clip_tail.active = False
