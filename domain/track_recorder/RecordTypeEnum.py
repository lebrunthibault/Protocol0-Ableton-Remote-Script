from typing import Type, TYPE_CHECKING

from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioExportOnce import \
    TrackRecorderExternalSynthAudioExportOnce

if TYPE_CHECKING:
    from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.shared.AbstractEnum import AbstractEnum


class RecordTypeEnum(AbstractEnum):
    MIDI = "MIDI"
    MIDI_UNLIMITED = "MIDI_UNLIMITED"
    AUDIO_EXPORT = "AUDIO_EXPORT"
    AUDIO_EXPORT_ONE = "AUDIO_EXPORT_ONE"
    AUDIO = "AUDIO"
    AUDIO_MULTI = "AUDIO_MULTI"

    @property
    def is_normal_recording(self):
        # type: () -> bool
        return self in (RecordTypeEnum.MIDI, RecordTypeEnum.MIDI_UNLIMITED)

    @property
    def need_additional_scene(self):
        # type: () -> bool
        return self == RecordTypeEnum.AUDIO_EXPORT

    @property
    def record_tail(self):
        # type: () -> bool
        return self in (
            RecordTypeEnum.AUDIO,
            RecordTypeEnum.AUDIO_EXPORT,
            RecordTypeEnum.AUDIO_EXPORT_ONE,
            RecordTypeEnum.MIDI,
        )

    @property
    def recorder_class(self):
        # type: () -> Type[AbstractTrackRecorder]
        from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import \
            TrackRecorderExternalSynthAudio
        from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioExport import \
            TrackRecorderExternalSynthAudioExport
        from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioMulti import \
            TrackRecorderExternalSynthAudioMulti
        from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthNormal import \
            TrackRecorderExternalSynthNormal

        return self.get_value_from_mapping(
            {
                RecordTypeEnum.AUDIO: TrackRecorderExternalSynthAudio,
                RecordTypeEnum.AUDIO_EXPORT: TrackRecorderExternalSynthAudioExport,
                RecordTypeEnum.AUDIO_EXPORT_ONE: TrackRecorderExternalSynthAudioExportOnce,
                RecordTypeEnum.AUDIO_MULTI: TrackRecorderExternalSynthAudioMulti,
                RecordTypeEnum.MIDI: TrackRecorderExternalSynthNormal,
                RecordTypeEnum.MIDI_UNLIMITED: TrackRecorderExternalSynthNormal,
            }
        )

    @property
    def count_in_class(self):
        # type: () -> Type[CountInInterface]
        from protocol0.domain.track_recorder.count_in.CountInOneBar import CountInOneBar
        from protocol0.domain.track_recorder.count_in.CountInShort import CountInShort

        if self.is_normal_recording:
            return CountInOneBar
        else:
            return CountInShort

    @property
    def use_midi_clip_length(self):
        # type: () -> bool
        return self in (
            RecordTypeEnum.AUDIO,
            RecordTypeEnum.AUDIO_EXPORT,
            RecordTypeEnum.AUDIO_EXPORT_ONE,
            RecordTypeEnum.AUDIO_MULTI,
        )
