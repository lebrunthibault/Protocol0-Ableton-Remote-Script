from typing import Optional

from protocol0.domain.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.application.faderfox.InterfaceState import InterfaceState
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.domain.track_recorder.count_in.count_in_one_bar import CountInOneBar
from protocol0.domain.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.recorder.track_recorder_simple import TrackRecorderSimple


class TrackRecorderSimpleFactory(AbstractTrackRecorderFactory):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        super(TrackRecorderSimpleFactory, self).__init__()
        self.track = track

    def create_count_in(self, _):
        # type: (RecordTypeEnum) -> CountInInterface
        return CountInOneBar(self.track)

    def _create_recorder(self, _, __):
        # type: (RecordTypeEnum, int) -> AbstractTrackRecorder
        return TrackRecorderSimple(self.track)

    def _get_recording_scene_index(self, _):
        # type: (RecordTypeEnum) -> Optional[int]
        for i in range(self.song.selected_scene.index, len(self.song.scenes)):
            if not self.track.clip_slots[i].clip:
                return i

        return None

    def get_recording_bar_length(self, _):
        # type: (RecordTypeEnum) -> int
        return InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value