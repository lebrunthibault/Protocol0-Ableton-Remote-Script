from typing import List

from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade


class TrackRepository(object):
    def find_simple_by_name(self, name):
        # type: (str) -> SimpleTrack
        for track in SongFacade.simple_tracks():
            if track.matches_name(name):
                return track

        raise Protocol0Warning("Couldn't find SimpleTrack %s" % name)

    def find_all_simple_sub_tracks(self, group_track):
        # type: (AbstractGroupTrack) -> List[SimpleTrack]
        sub_tracks = []
        for sub_track in group_track.sub_tracks:
            if isinstance(sub_track, SimpleTrack):
                sub_tracks.append(sub_track)
            elif isinstance(sub_track, AbstractGroupTrack):
                sub_tracks += self.find_all_simple_sub_tracks(sub_track)
            else:
                raise Protocol0Error("Unknown track type: %s" % sub_track)

        return sub_tracks
