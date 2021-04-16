from typing import List

from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.utils.UserMutableSequence import UserMutableSequence


class AbstractTrackList(UserMutableSequence):
    """ Manipulate a track list as an object """
    def __init__(self, abstract_tracks, *a, **k):
        # type: (List[AbstractTrack]) -> None
        super(AbstractTrackList, self).__init__(abstract_tracks, *a, **k)
        self._abstract_tracks = abstract_tracks

    def play_stop(self):
        if any(abstract_track.is_playing for abstract_track in self._abstract_tracks):
            [t.stop() for t in self._abstract_tracks]
        else:
            [t.play() for t in self._abstract_tracks]

    def toggle_solo(self):
        for t in self._abstract_tracks:
            t.solo = not t.solo

    def toggle_fold(self):
        self.parent.log_dev(self._abstract_tracks)
        fold = (any(not abstract_track.is_folded for abstract_track in self._abstract_tracks))
        [setattr(abstract_track, "is_folded", fold) for abstract_track in self._abstract_tracks]
