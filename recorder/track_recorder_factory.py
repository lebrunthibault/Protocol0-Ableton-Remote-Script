from protocol0.lom.AbstractObject import AbstractObject
from protocol0.recorder.track_recorder import TrackRecorder


class TrackRecorderFactory(AbstractObject):
    @classmethod
    def create_recorder(cls):
        # type: () -> TrackRecorder
        pass