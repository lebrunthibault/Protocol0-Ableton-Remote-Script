from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.utils.decorators import p0_subject_slot


class SimpleAudioTailTrack(SimpleAudioTrack):
    DEFAULT_NAME = "tail"

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        super(SimpleAudioTailTrack, self)._devices_listener()
        if len(self.devices):
            self.parent.songManager.tracks_listener()
