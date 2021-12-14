from protocol0.lom.track.live_track.AbletonAudioTrack import AbletonAudioTrack
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class SimpleNoneTrack(SimpleAudioTrack):
    # noinspection PyMissingConstructor
    def __init__(self, *a, **k):
        # type: () -> None
        self._track = AbletonAudioTrack()
        super(SimpleNoneTrack, self).__init__(track=self._track, *a, **k)
