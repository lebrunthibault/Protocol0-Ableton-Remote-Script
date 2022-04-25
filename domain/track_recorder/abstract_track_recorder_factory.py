from typing import Optional

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.shared.SongFacade import SongFacade


class AbstractTrackRecorderFactory(object):
    """ Abstract Factory """

    def create_recorder(self, record_type):
        # type: (RecordTypeEnum) -> AbstractTrackRecorder
        recorder = self._create_recorder(record_type)

        if recorder is None:
            raise Protocol0Error("Couldn't generate recorder in %s" % self)

        return recorder

    def create_count_in(self, record_type):
        # type: (RecordTypeEnum) -> CountInInterface
        raise NotImplementedError

    def _create_recorder(self, record_type):
        # type: (RecordTypeEnum) -> AbstractTrackRecorder
        raise NotImplementedError

    def get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        index = self._get_recording_scene_index(record_type)

        if index is not None and index != SongFacade.selected_scene().index:
            SongFacade.scenes()[index].select()

        return index

    def _get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        raise NotImplementedError

    def get_recording_bar_length(self, _):
        # type: (RecordTypeEnum) -> int
        raise NotImplementedError
