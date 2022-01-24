from protocol0.lom.AbstractObject import AbstractObject
from protocol0.sequence.Sequence import Sequence
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder


class TrackRecorderDecorator(AbstractTrackRecorder, AbstractObject):
    def __init__(self, recorder):
        # type: (AbstractTrackRecorder) -> None
        super(TrackRecorderDecorator, self).__init__(track=recorder.track)
        self.recorder = recorder
        self.track = recorder.track

    @property
    def recording_scene_index(self):
        # type: () -> int
        return self.recorder.recording_scene_index

    def set_recording_scene_index(self, recording_scene_index):
        # type: (int) -> None
        self.recorder.set_recording_scene_index(recording_scene_index)

    def pre_record(self):
        # type: () -> Sequence
        return self.recorder.pre_record()

    def record(self, bar_length):
        # type: (int) -> Sequence
        return self.recorder.record(bar_length)

    def post_audio_record(self):
        # type: () -> None
        return self.recorder.post_audio_record()

    def post_record(self):
        # type: () -> None
        return self.recorder.post_record()

    def cancel_record(self):
        # type: () -> None
        return self.recorder.cancel_record()
