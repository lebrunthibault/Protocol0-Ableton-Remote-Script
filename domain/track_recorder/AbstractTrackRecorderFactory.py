from typing import Optional, Type

from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface


class AbstractTrackRecorderFactory(object):
    """ Abstract Factory """

    def __init__(self, track, playback_component, recording_component, recording_bar_length):
        # type: (AbstractTrack, PlaybackComponent, RecordingComponent, int) -> None
        self.track = track
        self._playback_component = playback_component
        self._recording_component = recording_component
        self._recording_bar_length = recording_bar_length

    def create_recorder(self, record_type):
        # type: (RecordTypeEnum) -> AbstractTrackRecorder
        recorder = self._get_recorder_class(record_type)(self.track, self._playback_component, self._recording_component)

        if recorder is None:
            raise Protocol0Error("Couldn't generate recorder in %s" % self)

        return recorder

    def create_count_in(self, record_type):
        # type: (RecordTypeEnum) -> CountInInterface
        return self._get_count_in_class(record_type)(self.track, self._playback_component)

    def _get_count_in_class(self, record_type):
        # type: (RecordTypeEnum) -> Type[CountInInterface]
        raise NotImplementedError

    def _get_recorder_class(self, record_type):
        # type: (RecordTypeEnum) -> Type[AbstractTrackRecorder]
        raise NotImplementedError

    def get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        raise NotImplementedError

    def get_recording_bar_length(self, _):
        # type: (RecordTypeEnum) -> int
        raise NotImplementedError
