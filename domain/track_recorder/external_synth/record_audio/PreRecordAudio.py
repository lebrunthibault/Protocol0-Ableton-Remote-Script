from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.external_synth.ExtAudioRecordingStartedEvent import \
    ExtAudioRecordingStartedEvent


class PreRecordAudio(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        track.monitoring_state.monitor_midi()
        midi_clip = track.midi_track.clip_slots[config.scene_index].clip
        if midi_clip.loop.start != 0:
            Backend.client().show_warning("Cropping midi clip")
            midi_clip.crop()
        DomainEventBus.emit(ExtAudioRecordingStartedEvent(track))
