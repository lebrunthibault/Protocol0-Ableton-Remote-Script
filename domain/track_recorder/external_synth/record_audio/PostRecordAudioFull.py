from functools import partial

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.external_synth.record_audio.PostRecordAudio import \
    PostRecordAudio
from protocol0.shared.SongFacade import SongFacade


class PostRecordAudioFull(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        PostRecordAudio().process(track, config)
        audio_clip = track.audio_track.clip_slots[config.scene_index].clip
        audio_clip.looping = False
        Scheduler.defer(partial(self._edit_loop, audio_clip, config.bar_length))

    def _edit_loop(self, audio_clip, bar_length):
        # type: (AudioClip, int) -> None
        audio_clip.loop.end = bar_length * SongFacade.signature_numerator()
        audio_clip.loop.start_marker = 0
        audio_clip.loop.start = (bar_length / 2) * SongFacade.signature_numerator()
        audio_clip.looping = True
