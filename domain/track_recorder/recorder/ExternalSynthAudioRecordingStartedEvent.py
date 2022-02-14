from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ExternalSynthAudioRecordingStartedEvent(object):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        self.track = track
