from typing import List

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class AbstractTrackList(list, AbstractObject):
    """
        Making actions on a list of selected_tracks
    """
    def __init__(self, abstract_tracks, *a, **k):
        # type: (List[AbstractTrack]) -> None
        super(AbstractTrackList, self).__init__(*a, **k)
        self._abstract_tracks = abstract_tracks

    def play_stop(self):
        if any([abstract_track.is_playing for abstract_track in self._abstract_tracks]):
            [t.stop() for t in self._abstract_tracks]
        else:
            [t.play() for t in self._abstract_tracks]

    def solo(self):
        [t.action_solo() for t in self._abstract_tracks]


