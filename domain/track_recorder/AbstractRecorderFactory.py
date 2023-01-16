from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum


class AbstractTrackRecorderFactory(object):
    """Abstract Factory"""
    def get_recorder_config(self, track, record_type, recording_bar_length):
        # type: (AbstractTrack, RecordTypeEnum, int) -> RecordConfig
        raise NotImplementedError
