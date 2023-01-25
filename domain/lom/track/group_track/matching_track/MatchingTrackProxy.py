from typing import Optional, cast

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


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

class MatchingTrackProxy(Observable):
    """Shared wrapper around an optional audio track"""
    def __init__(self, base_track):
        # type: (SimpleTrack) -> None
        super(MatchingTrackProxy, self).__init__()
        self.base_track = base_track
        self.audio_track = cast(SimpleAudioTrack, _get_audio_track(self.base_track))
        assert self.audio_track is not None, "no matching track found"
        self.notify_observers()
