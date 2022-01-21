from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.track_recorder.decorator.track_recorder_decorator import TrackRecorderDecorator
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder


class AbstractTrackRecorderExternalSynthDecorator(TrackRecorderDecorator):
    def __init__(self, recorder):
        # type: (AbstractTrackRecorder) -> None
        super(AbstractTrackRecorderExternalSynthDecorator, self).__init__(recorder=recorder)
        self.track = self.track  # type: ExternalSynthTrack
