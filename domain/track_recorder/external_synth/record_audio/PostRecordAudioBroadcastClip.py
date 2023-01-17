from functools import partial

from typing import Optional, cast

from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.shared.sequence.Sequence import Sequence


class PostRecordAudioBroadcastClip(RecordProcessorInterface):
    def __init__(self, post_record):
        # type: (RecordProcessorInterface) -> None
        self._post_record = post_record

    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> Optional[Sequence]
        self._post_record.process(track, config)

        seq = Sequence()
        seq.wait(11)

        seq.add(partial(self._broadcast_clip, track.audio_track, config.scene_index))

        return seq.done()

    def _broadcast_clip(self, track, scene_index):
        # type: (SimpleAudioTrack, int) -> Optional[Sequence]
        source_cs = track.clip_slots[scene_index]

        matching_track = cast(ExternalSynthTrack, track.abstract_track).matching_track._track

        if matching_track is None:
            return None

        matching_clip_slots = [cs for cs in matching_track.clip_slots if source_cs.matches(cs)]

        seq = Sequence()
        for clip_slot in matching_clip_slots:
            device_params = matching_track.devices.parameters
            automated_params = clip_slot.clip.automation.get_automated_parameters(device_params)

            # duplicate when no automation else manual action is needed
            if len(automated_params) == 0:
                clip_slot.replace_clip_sample(clip_slot)
            else:
                seq.add(partial(clip_slot.replace_clip_sample, None, source_cs.clip.file_path))

        seq.add(partial(Backend.client().close_explorer_window, "Recorded"))
        seq.add(
            partial(Backend.client().show_success, "%s clips replaced" % len(matching_clip_slots))
        )

        return seq.done()
