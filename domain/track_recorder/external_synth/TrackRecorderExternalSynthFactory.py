from typing import Optional

from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.AbstractRecorderFactory import (
    AbstractTrackRecorderFactory,
)
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.config.RecordProcessors import RecordProcessors
from protocol0.domain.track_recorder.external_synth.OnRecordEndClipTail import OnRecordEndClipTail
from protocol0.domain.track_recorder.external_synth.record_audio.PostRecordAudio import (
    PostRecordAudio,
)
from protocol0.domain.track_recorder.external_synth.record_audio.PostRecordAudioFull import (
    PostRecordAudioFull,
)
from protocol0.domain.track_recorder.external_synth.record_audio.PreRecordAudio import (
    PreRecordAudio,
)
from protocol0.domain.track_recorder.external_synth.record_audio.record_multi.PreRecordAudioMulti import (
    PreRecordAudioMulti,
)
from protocol0.domain.track_recorder.external_synth.record_audio.record_multi.RecordAudioMulti import (
    RecordAudioMulti,
)
from protocol0.domain.track_recorder.external_synth.record_midi.PostRecordMidi import PostRecordMidi
from protocol0.domain.track_recorder.external_synth.record_midi.PreRecordMidi import PreRecordMidi
from protocol0.shared.Song import Song


class TrackRecorderExternalSynthFactory(AbstractTrackRecorderFactory):
    def get_record_config(self, track, record_type, recording_bar_length):
        # type: (ExternalSynthTrack, RecordTypeEnum, int) -> RecordConfig
        tracks = [track.audio_track]
        if record_type.records_midi:
            tracks.insert(0, track.midi_track)
        scene_index = self._get_scene_index(track, record_type)
        bar_length = self._get_bar_length(track, record_type, recording_bar_length)

        return RecordConfig(
            record_name=record_type.value,
            tracks=tracks,
            scene_index=scene_index,
            bar_length=bar_length,
            records_midi=record_type.records_midi,
        )

    def _get_scene_index(self, track, record_type):
        # type: (ExternalSynthTrack, RecordTypeEnum) -> Optional[int]
        if record_type.records_midi:
            for i in range(Song.selected_scene().index, len(Song.scenes())):
                if (
                    not track.midi_track.clip_slots[i].clip
                    and not track.audio_track.clip_slots[i].clip
                ):
                    return i

            return None
        else:
            if not track.midi_track.clip_slots[Song.selected_scene().index].clip is not None:
                raise Protocol0Warning("No midi clip selected")
            return Song.selected_scene().index

    def _get_bar_length(self, track, record_type, bar_length):
        # type: (ExternalSynthTrack, RecordTypeEnum, int) -> int
        midi_bar_length = 0
        if not record_type.records_midi:
            midi_clip = track.midi_track.clip_slots[Song.selected_scene().index].clip
            midi_bar_length = int(midi_clip.bar_length)

        return {
            RecordTypeEnum.MIDI: bar_length,
            RecordTypeEnum.MIDI_UNLIMITED: 0,
            RecordTypeEnum.AUDIO: midi_bar_length,
            RecordTypeEnum.AUDIO_FULL: midi_bar_length * 2,
            RecordTypeEnum.AUDIO_MULTI_SCENE: midi_bar_length,
        }[record_type]

    def get_processors(self, record_type):
        # type: (RecordTypeEnum) -> RecordProcessors
        midi_processor_config = RecordProcessors(
            pre_record=PreRecordMidi(), post_record=PostRecordMidi()
        )
        audio_processor_config = RecordProcessors(
            pre_record=PreRecordAudio(),
            on_record_end=OnRecordEndClipTail(),
            post_record=PostRecordAudio(),
        )
        audio_full_processor_config = audio_processor_config.copy()
        audio_full_processor_config.post_record = PostRecordAudioFull()

        audio_processor_config_multi = RecordProcessors(
            pre_record=PreRecordAudioMulti(),
            record=RecordAudioMulti(),
            on_record_end=OnRecordEndClipTail(),
        )

        return {
            RecordTypeEnum.MIDI: midi_processor_config,
            RecordTypeEnum.MIDI_UNLIMITED: midi_processor_config,
            RecordTypeEnum.AUDIO: audio_processor_config,
            RecordTypeEnum.AUDIO_FULL: audio_full_processor_config,
            RecordTypeEnum.AUDIO_MULTI_SCENE: audio_processor_config_multi,
        }[record_type]
