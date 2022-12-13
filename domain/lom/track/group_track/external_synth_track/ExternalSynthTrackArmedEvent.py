from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class ExternalSynthTrackArmedEvent(object):
    def __init__(self, track, arm=True):
        # type: (SimpleAudioTrack, bool) -> None
        self.track = track
        self.arm = arm
