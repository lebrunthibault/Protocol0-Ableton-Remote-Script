from _Framework.SubjectSlot import SlotManager
from typing import TYPE_CHECKING

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipManager import \
    MatchingTrackClipManager
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackProxy import \
    MatchingTrackProxy
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackRouter import \
    MatchingTrackRouter
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackSoloState import \
    MatchingTrackSoloState
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class MatchingTrackInterface(SlotManager):
    def __init__(self, base_track):
        # type: (SimpleTrack) -> None
        super(MatchingTrackInterface, self).__init__()
        self._track_proxy = MatchingTrackProxy(base_track)
        self.router = MatchingTrackRouter(self._track_proxy)
        self._solo_state = MatchingTrackSoloState(self._track_proxy)
        self.clip_manager = MatchingTrackClipManager(self._track_proxy)

    def __repr__(self):
        # type: () -> str
        return "MatchingTrack(%s => %s)" % (self._track_proxy.base_track, self._track_proxy.audio_track)

    def bounce(self):
        # type: () -> Sequence
        raise NotImplementedError
