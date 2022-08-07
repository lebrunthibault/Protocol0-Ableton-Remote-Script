import collections

from typing import Dict

from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.shared.SongFacade import SongFacade


class TrackStats(object):
    def __init__(self):
        # type: () -> None
        self.count = len(list(SongFacade.simple_tracks()))
        self.abstract_track_count = len(
            [
                track
                for track in SongFacade.abstract_tracks()
                if not isinstance(track, NormalGroupTrack)
            ]
        )
        self.ext_synth_track_count = len(list(SongFacade.external_synth_tracks()))

    def to_dict(self):
        # type: () -> Dict
        output = collections.OrderedDict()
        output["track count"] = self.count
        output["abstract track count"] = self.abstract_track_count
        output["ext-synth track count"] = self.ext_synth_track_count

        return output
