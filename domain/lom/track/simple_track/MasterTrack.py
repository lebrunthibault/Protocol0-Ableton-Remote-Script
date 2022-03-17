from protocol0.domain.lom.track.TrackColorEnum import TrackColorEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class MasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False
    DEFAULT_COLOR = TrackColorEnum.DISABLED
