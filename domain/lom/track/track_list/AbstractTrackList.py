from typing import Iterable, Iterator

from protocol0.domain.lom.track.TrackComponent import TrackComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class AbstractTrackList(TrackComponent):
    """ Manipulate a track list as an object """

    def __init__(self, abstract_tracks):
        # type: (Iterable[AbstractTrack]) -> None
        tracks = list(dict.fromkeys(abstract_tracks))
        self._abstract_tracks = tracks

    def __iter__(self):
        # type: () -> Iterator[AbstractTrack]
        return iter(self._abstract_tracks)

    @property
    def abstract_group_tracks(self):
        # type: () -> Iterable[AbstractGroupTrack]
        return (ab for ab in self._abstract_tracks if isinstance(ab, AbstractGroupTrack))

    def fold(self):
        # type: () -> None
        for abg in self.abstract_group_tracks:
            abg.fold()
