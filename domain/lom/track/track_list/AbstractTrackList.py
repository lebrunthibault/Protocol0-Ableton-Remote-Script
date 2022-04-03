from typing import Iterable, Iterator

from protocol0.domain.lom.track.TrackComponent import TrackComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack


class AbstractTrackList(TrackComponent):
    """Composite pattern : manipulate a track list as an object"""

    def __init__(self, abstract_tracks):
        # type: (Iterable[AbstractTrack]) -> None
        tracks = list(dict.fromkeys(abstract_tracks))
        self._tracks = tracks

    def __iter__(self):
        # type: () -> Iterator[AbstractTrack]
        return iter(self._tracks)

    def fold(self):
        # type: () -> None
        for abg in self._tracks:
            abg.fold()
