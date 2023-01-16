from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.external_synth.ExternalSynthAudioRecordingEndedEvent import \
    ExternalSynthAudioRecordingEndedEvent
from protocol0.shared.SongFacade import SongFacade


class PostRecordAudio(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        DomainEventBus.emit(ExternalSynthAudioRecordingEndedEvent(track))

        audio_clip = track.audio_track.clip_slots[config.scene_index].clip
        audio_clip.looping = True
        audio_clip.loop.end = config.bar_length * SongFacade.signature_numerator()
        audio_clip.clip_name.update("")
