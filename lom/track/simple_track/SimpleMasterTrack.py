from protocol0.enums.ColorEnum import ColorEnum
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class SimpleMasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False
    DEFAULT_COLOR = ColorEnum.DISABLED
