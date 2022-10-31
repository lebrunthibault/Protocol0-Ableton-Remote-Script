from typing import Optional, Any, cast, Type

from protocol0.domain.lom.track.simple_track.ResamplingTrack import ResamplingTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.AbstractTrackRecorderFactory import (
    AbstractTrackRecorderFactory,
)
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.simple.TrackRecorderSimple import TrackRecorderSimple
from protocol0.shared.SongFacade import SongFacade


class TrackRecorderSimpleFactory(AbstractTrackRecorderFactory):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderSimpleFactory, self).__init__(*a, **k)
        self.track = cast(SimpleTrack, self.track)

    def _get_recorder_class(self, _):
        # type: (RecordTypeEnum) -> Type[AbstractTrackRecorder]
        return TrackRecorderSimple

    def get_recording_scene_index(self, _):
        # type: (RecordTypeEnum) -> Optional[int]
        for i in range(SongFacade.selected_scene().index, len(SongFacade.scenes())):
            if not self.track.clip_slots[i].clip:
                return i

        return None

    def get_recording_bar_length(self, record_type):
        # type: (RecordTypeEnum) -> int
        if record_type == RecordTypeEnum.NORMAL_UNLIMITED:
            return 0
        elif record_type == RecordTypeEnum.NORMAL:
            return self._recording_bar_length
        elif record_type == RecordTypeEnum.AUDIO_ONLY and isinstance(SongFacade.selected_track(), ResamplingTrack):
            return SongFacade.selected_scene().bar_length
        else:
            raise Protocol0Warning("Invalid record type")
