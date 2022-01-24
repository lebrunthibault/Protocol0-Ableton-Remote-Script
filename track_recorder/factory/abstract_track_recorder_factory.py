from typing import Optional

from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.track_recorder.decorator.track_recorder_count_in_one_bar_decorator import \
    TrackRecorderCountInOneBarDecorator
from protocol0.track_recorder.decorator.track_recorder_count_in_short_decorator import \
    TrackRecorderCountInShortDecorator
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder


class AbstractTrackRecorderFactory(AbstractObject):
    def create_recorder(self, record_type, recording_scene_index, bar_length):
        # type: (RecordTypeEnum, int, int) -> AbstractTrackRecorder
        recorder = self._create_recorder(record_type, bar_length)
        recorder.set_recording_scene_index(recording_scene_index)

        if recorder is None:
            raise Protocol0Error("Couldn't generate recorder")

        # apply common decorators
        if record_type == RecordTypeEnum.NORMAL:
            recorder = TrackRecorderCountInOneBarDecorator(recorder)
        else:
            recorder = TrackRecorderCountInShortDecorator(recorder)

        return recorder

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
