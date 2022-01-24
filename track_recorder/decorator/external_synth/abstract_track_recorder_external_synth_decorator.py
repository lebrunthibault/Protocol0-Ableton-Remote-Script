from protocol0.track_recorder.decorator.track_recorder_decorator import TrackRecorderDecorator
from protocol0.track_recorder.recorder.abstract_track_recorder_external_synth import AbstractTrackRecorderExternalSynth


class AbstractTrackRecorderExternalSynthDecorator(TrackRecorderDecorator):
    def __init__(self, recorder):
        # type: (AbstractTrackRecorderExternalSynth) -> None
        super(AbstractTrackRecorderExternalSynthDecorator, self).__init__(recorder=recorder)
        self.track = recorder.track
