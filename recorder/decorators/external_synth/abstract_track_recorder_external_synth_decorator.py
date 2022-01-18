from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.recorder.decorators.track_recorder_decorator import TrackRecorderDecorator
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface


class AbstractTrackRecorderExternalSynthDecorator(TrackRecorderDecorator):
    def __init__(self, recorder):
        # type: (TrackRecorderInterface) -> None
        super(AbstractTrackRecorderExternalSynthDecorator, self).__init__(recorder=recorder)
        self.track = self.track  # type: ExternalSynthTrack
