from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class ExtArmedEvent(object):
    def __init__(self, track, arm=True):
        # type: (SimpleAudioTrack, bool) -> None
        self.track = track
        self.arm = arm
