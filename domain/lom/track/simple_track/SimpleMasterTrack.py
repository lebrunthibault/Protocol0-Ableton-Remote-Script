from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class SimpleMasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False
    DEFAULT_COLOR = ColorEnum.DISABLED
