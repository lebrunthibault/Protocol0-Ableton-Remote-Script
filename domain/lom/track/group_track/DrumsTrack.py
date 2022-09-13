from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class DrumsTrack(NormalGroupTrack):
    TRACK_NAME = "Drums"

    @classmethod
    def is_track_valid(cls, track):
        # type: (SimpleTrack) -> bool
        return track.name.split(" ")[0] == cls.TRACK_NAME
