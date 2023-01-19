from functools import partial

from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.external_synth.ExtAudioRecordingEndedEvent import (
    ExtAudioRecordingEndedEvent,
)
from protocol0.shared.Song import Song


class PostRecordAudio(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        DomainEventBus.emit(ExtAudioRecordingEndedEvent(track))

        midi_clip = track.midi_track.clip_slots[config.scene_index].clip
        audio_clip = track.audio_track.clip_slots[config.scene_index].clip
        assert audio_clip, "No recorded audio clip"

        audio_clip.looping = True
        # fix Live setting the loop to infinite
        Scheduler.wait(
            10,
            partial(
                setattr, audio_clip.loop, "end", config.bar_length * Song.signature_numerator()
            ),
        )
        track.audio_track.set_clip_midi_hash(audio_clip, midi_clip.hash)
        audio_clip.clip_name.update(midi_clip.clip_name.base_name)
