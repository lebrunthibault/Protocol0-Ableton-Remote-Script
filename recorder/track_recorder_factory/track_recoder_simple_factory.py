from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.recorder.track_recorder_factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface
from protocol0.recorder.track_recorder_simple import TrackRecorderSimple


class TrackRecorderSimpleFactory(AbstractTrackRecorderFactory):
    @classmethod
    def create_recorder(cls, track, _, __):
        # type: (SimpleTrack, RecordTypeEnum, BarLengthEnum) -> TrackRecorderInterface
        """ breaking lsp """
        return TrackRecorderSimple(track)
