from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack


class TrackComponent(object):
    def __iter__(self):
        # type: () -> Iterator[AbstractTrack]
        raise NotImplementedError

    def fold(self):
        # type: () -> None
        raise NotImplementedError
