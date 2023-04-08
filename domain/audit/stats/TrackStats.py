import collections

from typing import Dict

from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.midi.special.UsamoTrack import UsamoTrack
from protocol0.shared.Song import Song


class TrackStats(object):
    def __init__(self):
        # type: () -> None
        excluded_track_classes = (NormalGroupTrack, UsamoTrack)
        tracks = [t for t in Song.abstract_tracks() if not isinstance(t, excluded_track_classes)]
        tracks_sorted = sorted(tracks, key=lambda track: track.load_time)
        self._slow_tracks = [t for t in list(reversed(tracks_sorted))[0:10] if t.load_time]

    def to_dict(self):
        # type: () -> Dict
        output = collections.OrderedDict()
        output["slow tracks"] = ["%s: %s ms" % (t.name, t.load_time) for t in self._slow_tracks]

        return output
