from typing import List

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.external_synth.ExtAudioRecordingStartedEvent import (
    ExtAudioRecordingStartedEvent,
)
from protocol0.domain.track_recorder.external_synth.record_audio.PreRecordAudio import \
    PreRecordAudio


class PreRecordAudioMulti(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        """
        Alerting when a midi clip does not have the same bar length as its scene (except for the last one)
        In this case the audio tail might not be recorded fully due to switching scenes

        This is not usual practice the case but could be addressed by using
        the clip tail decorator to delay the recording of the next scene
        """
        PreRecordAudio().process(track, config)

        midi_clip = track.midi_track.clip_slots[config.scene_index].clip
        if midi_clip.loop.start != 0:
            Backend.client().show_warning("Cropping midi clip")
            midi_clip.crop()
        DomainEventBus.emit(ExtAudioRecordingStartedEvent(track))

        scene_clip_bar_length_mismatch = False
        for scene in self._recording_scenes(track, config)[:-1]:
            if scene.bar_length != track.midi_track.clip_slots[scene.index].clip.bar_length:
                scene_clip_bar_length_mismatch = True
                break

        if scene_clip_bar_length_mismatch:
            Backend.client().show_warning(
                "At least one midi clip has a smaller bar length than its scene. Pay attention to the tail recording"
            )

    def _recording_scenes(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> List[Scene]
        """A list of scenes that are going to be recorded"""
        scenes = [config.recording_scene]
        while (
            config.recording_scene.next_scene != scenes[-1]
            and track.midi_track.clip_slots[scenes[-1].next_scene.index].clip
        ):
            scenes.append(scenes[-1].next_scene)

        return scenes
