from typing import List, Optional

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.config.RecordProcessorConfig import RecordProcessorConfig
from protocol0.shared.SongFacade import SongFacade


class RecordConfig(object):
    def __init__(
        self,
        record_name,  # type: str
        tracks,  # type: List[SimpleTrack]
        scene_index,  # type: Optional[int]
        bar_length,  # type: int
        records_midi,  # type: bool
        processor_config,  # type: RecordProcessorConfig
    ):
        # type: (...) -> None
        self.record_name = record_name
        self.tracks = tracks
        self._scene_index = scene_index
        self.bar_length = bar_length
        self.records_midi = records_midi

        # processors
        self._processor_config = processor_config
        self.pre_record_processor = processor_config.pre_record_processor
        self.record_processor = processor_config.record_processor
        self.on_record_end_processor = processor_config.on_record_end_processor
        self.post_record_processor = processor_config.post_record_processor

    @property
    def scene_index(self):
        # type: () -> int
        assert self._scene_index is not None, "No recording scene index"
        return self._scene_index

    @scene_index.setter
    def scene_index(self, scene_index):
        # type: (int) -> None
        self._scene_index = scene_index

    @property
    def recording_scene(self):
        # type: () -> Scene
        return SongFacade.scenes()[self.scene_index]

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return [track.clip_slots[self.scene_index] for track in self.tracks]

    def __repr__(self):
        # type: () -> str
        # noinspection SpellCheckingInspection
        return (
            "RecordConfig(\nrecord_name=%s,\ntracks=%s,\nscene_index=%s,\nbar_length=%s\nrecords_midi=%s,\nprocessor_config=%s"
            % (
                self.record_name,
                self.tracks,
                self.scene_index,
                self.bar_length,
                self.records_midi,
                self._processor_config,
            )
        )
