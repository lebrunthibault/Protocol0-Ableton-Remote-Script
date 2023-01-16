from functools import partial

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig


class PostRecordSimple(RecordProcessorInterface):
    def process(self, track, config):
        # type: (SimpleTrack, RecordConfig) -> None
        # deferring because the clip length is not accurate right now
        Scheduler.wait_ms(
            50, partial(track.clip_slots[config.scene_index].clip.post_record, config.bar_length)
        )
