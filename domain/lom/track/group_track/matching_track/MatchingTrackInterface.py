from _Framework.SubjectSlot import SlotManager
from typing import TYPE_CHECKING, cast, Optional

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipColorManager import \
    MatchingTrackClipColorManager
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipManager import \
    MatchingTrackClipManager
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackRouter import \
    MatchingTrackRouter
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackSoloState import \
    MatchingTrackSoloState
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
def _get_audio_track(base_track):
    # type: (SimpleTrack) -> Optional[SimpleAudioTrack]
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

    return find_if(
        lambda t: t != base_track
                  and t.index != base_track.index  # when multiple objects for the same track
                  and not t.is_foldable
                  and t.name == base_track.name,
        Song.simple_tracks(SimpleAudioTrack),
    )


class MatchingTrackInterface(SlotManager):
    def __init__(self, base_track):
        # type: (SimpleTrack) -> None
        super(MatchingTrackInterface, self).__init__()
        self._base_track = base_track
        self._audio_track = cast(SimpleAudioTrack, _get_audio_track(base_track))
        assert self._audio_track is not None, "no matching track found"

        self.router = MatchingTrackRouter(base_track, self._audio_track)
        self._solo_state = MatchingTrackSoloState(base_track, self._audio_track)
        self.clip_manager = MatchingTrackClipManager(self.router, base_track, self._audio_track)

    def __repr__(self):
        # type: () -> str
        return "MatchingTrack(%s => %s)" % (self._base_track, self._audio_track)

    @property
    def clip_color_manager(self):
        # type: () -> MatchingTrackClipColorManager
        raise NotImplementedError

    def bounce(self):
        # type: () -> Sequence
        raise NotImplementedError
