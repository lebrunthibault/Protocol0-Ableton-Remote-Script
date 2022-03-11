from typing import Optional

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.SongFacade import SongFacade


class TrackRepository(object):
    def get_by_name(self, name):
        # type: (str) -> Optional[SimpleTrack]
        for track in SongFacade.simple_tracks():
            first_word = track.name.split(" ")[0].lower()
            if first_word == name.lower():
                return track

        return None
