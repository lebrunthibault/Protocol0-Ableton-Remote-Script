from typing import Optional, TYPE_CHECKING, Any

from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrackClips import \
    SimpleAudioTrackClips
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence

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

    def _post_flatten(self, clip_infos):
        # type: (SimpleAudioTrackClips) -> Optional[Sequence]
        super(SimpleAudioExtTrack, self)._post_flatten(clip_infos)
        flattened_track = Song.selected_track(SimpleAudioTrack)

        abstract_track = flattened_track.abstract_track
        # for the linter. we know it's an ext track
        if hasattr(abstract_track, "matching_track"):
            return abstract_track.matching_track.broadcast_clips(clip_infos, flattened_track)

        return None