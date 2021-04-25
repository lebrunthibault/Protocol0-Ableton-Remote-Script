from typing import Any, Iterable

from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.utils.UserMutableSequence import UserMutableSequence


class AbstractTrackList(UserMutableSequence):
    """ Manipulate a track list as an object """

    def __init__(self, abstract_tracks, *a, **k):
        # type: (Iterable[AbstractTrack], Any, Any) -> None
        super(AbstractTrackList, self).__init__(list=list(abstract_tracks), *a, **k)
        self._abstract_tracks = list(abstract_tracks)

    def play_stop(self):
        # type: () -> None
        if any(abstract_track.is_playing for abstract_track in self._abstract_tracks):
            for t in self._abstract_tracks:
                t.stop()
        else:
            for t in self._abstract_tracks:
                t.play()

    def toggle_solo(self):
        # type: () -> None
        for t in self._abstract_tracks:
            t.solo = not t.solo

    def toggle_fold(self):
        # type: () -> None
        should_fold = any(
            abstract_track.is_foldable and not abstract_track.is_folded for abstract_track in self._abstract_tracks
        )
        for abstract_track in self._abstract_tracks:
            abstract_track.is_folded = should_fold
