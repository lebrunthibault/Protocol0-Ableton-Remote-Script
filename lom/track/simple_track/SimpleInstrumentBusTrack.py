from protocol0.enums.ColorEnum import ColorEnum
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class SimpleInstrumentBusTrack(SimpleAudioTrack):
    DEFAULT_NAME = "Instrument bus"
    DEFAULT_COLOR = ColorEnum.DISABLED

    def _added_track_init(self):
        # type: () -> None
        pass
