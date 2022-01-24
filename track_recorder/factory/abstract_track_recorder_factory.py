from typing import Optional

from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder


class AbstractTrackRecorderFactory(AbstractObject):
    def create_recorder(self, record_type, bar_length):
        # type: (RecordTypeEnum, int) -> AbstractTrackRecorder
        recorder = self._create_recorder(record_type, bar_length)

        if recorder is None:
            raise Protocol0Error("Couldn't generate recorder")

        return recorder

    def create_count_in(self, record_type):
        # type: (RecordTypeEnum) -> CountInInterface
        raise NotImplementedError

    def _create_recorder(self, record_type, bar_length):
        # type: (RecordTypeEnum, int) -> AbstractTrackRecorder
        raise NotImplementedError

    def get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        index = self._get_recording_scene_index(record_type=record_type)

        if index is not None and index != self.song.selected_scene.index:
            self.song.scenes[index].select()

        return index

    def _get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        raise NotImplementedError

    def get_recording_bar_length(self, _):
        # type: (RecordTypeEnum) -> int
        raise NotImplementedError
