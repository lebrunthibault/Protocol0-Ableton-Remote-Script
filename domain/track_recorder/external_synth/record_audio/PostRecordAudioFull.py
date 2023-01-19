from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.external_synth.record_audio.PostRecordAudio import \
    PostRecordAudio
from protocol0.shared.Song import Song


class PostRecordAudioFull(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        PostRecordAudio().process(track, config)

        audio_clip = track.audio_track.clip_slots[config.scene_index].clip
        audio_clip.looping = False
        audio_clip.loop.end = config.bar_length * Song.signature_numerator()
        audio_clip.loop.start_marker = 0
        audio_clip.loop.start = (config.bar_length / 2) * Song.signature_numerator()
        audio_clip.looping = True
