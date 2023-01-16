from typing import Optional

from protocol0.domain.lom.track.simple_track.ResamplingTrack import ResamplingTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.AbstractRecorderFactory import (
    AbstractTrackRecorderFactory,
)
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.config.RecordProcessorConfig import RecordProcessorConfig
from protocol0.domain.track_recorder.simple.PostRecordSimple import PostRecordSimple
from protocol0.shared.SongFacade import SongFacade


class TrackRecorderSimpleFactory(AbstractTrackRecorderFactory):
    def get_recorder_config(self, track, record_type, recording_bar_length):
        # type: (SimpleTrack, RecordTypeEnum, int) -> RecordConfig
        return RecordConfig(
            record_name=record_type.value,
            tracks=[track],
            scene_index=self._get_recording_scene_index(track),
            bar_length=self._get_recording_bar_length(record_type, recording_bar_length),
            records_midi=True,
            processor_config=RecordProcessorConfig(post_record_processor=PostRecordSimple())
        )

    def _get_recording_scene_index(self, track):
        # type: (SimpleTrack) -> Optional[int]
        for i in range(SongFacade.selected_scene().index, len(SongFacade.scenes())):
            if not track.clip_slots[i].clip:
                return i

        return None

    def _get_recording_bar_length(self, record_type, bar_length):
        # type: (RecordTypeEnum, int) -> int
        if record_type == RecordTypeEnum.MIDI_UNLIMITED:
            return 0
        elif record_type == RecordTypeEnum.MIDI:
            return bar_length
        elif record_type == RecordTypeEnum.AUDIO and isinstance(
            SongFacade.selected_track(), ResamplingTrack
        ):
            return SongFacade.selected_scene().bar_length
        else:
            raise Protocol0Warning("Invalid record type")
