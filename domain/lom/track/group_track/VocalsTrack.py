from protocol0.domain.lom.track.TrackColorEnum import TrackColorEnum
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack


class VocalsTrack(NormalGroupTrack):
    TRACK_NAME = "Vocals"
    DEFAULT_COLOR = TrackColorEnum.VOCALS
