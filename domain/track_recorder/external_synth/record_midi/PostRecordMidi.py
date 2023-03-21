from functools import partial

from typing import cast

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface


class PostRecordMidi(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        track.monitoring_state.monitor_midi()

        midi_clip = cast(MidiClip, track.midi_track.clip_slots[config.scene_index].clip)
        midi_clip.clip_name.update("")
        # deferring because the clip length is not accurate right now
        Scheduler.wait_ms(50, partial(midi_clip.post_record, config.bar_length))

        audio_clip = track.audio_track.clip_slots[config.scene_index].clip
        assert audio_clip, "No recorded audio clip"

        audio_clip.clip_name.update("")
        track.audio_track.clip_mapping.register_file_path(
            audio_clip.file_path, ClipInfo(midi_clip, track.midi_track.devices.parameters)
        )
        audio_clip.appearance.color = ClipColorEnum.AUDIO_UN_QUANTIZED.value
