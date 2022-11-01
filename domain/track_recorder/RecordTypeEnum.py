from typing import Type, TYPE_CHECKING

from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioExportOnce import \
    TrackRecorderExternalSynthAudioExportOnce

if TYPE_CHECKING:
    from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.shared.AbstractEnum import AbstractEnum


class RecordTypeEnum(AbstractEnum):
    NORMAL = "NORMAL"
    NORMAL_UNLIMITED = "NORMAL_UNLIMITED"
    AUDIO_ONLY = "AUDIO_ONLY"
    AUDIO_ONLY_EXPORT = "AUDIO_ONLY_EXPORT"
    AUDIO_ONLY_EXPORT_ONE = "AUDIO_ONLY_EXPORT_ONE"
    AUDIO_ONLY_MULTI = "AUDIO_ONLY_MULTI"

    @property
    def is_normal_recording(self):
        # type: () -> bool
        return self in (RecordTypeEnum.NORMAL, RecordTypeEnum.NORMAL_UNLIMITED)

    @property
    def need_additional_scene(self):
        # type: () -> bool
        return self == RecordTypeEnum.AUDIO_ONLY_EXPORT

    @property
    def record_tail(self):
        # type: () -> bool
        return self in (
            RecordTypeEnum.AUDIO_ONLY_EXPORT,
            RecordTypeEnum.AUDIO_ONLY_EXPORT_ONE,
            RecordTypeEnum.NORMAL,
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
        from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthNormalUnlimited import \
            TrackRecorderExternalSynthNormalUnlimited

        return self.get_value_from_mapping(
            {
                RecordTypeEnum.AUDIO_ONLY: TrackRecorderExternalSynthAudio,
                RecordTypeEnum.AUDIO_ONLY_EXPORT: TrackRecorderExternalSynthAudioExport,
                RecordTypeEnum.AUDIO_ONLY_EXPORT_ONE: TrackRecorderExternalSynthAudioExportOnce,
                RecordTypeEnum.AUDIO_ONLY_MULTI: TrackRecorderExternalSynthAudioMulti,
                RecordTypeEnum.NORMAL: TrackRecorderExternalSynthNormal,
                RecordTypeEnum.NORMAL_UNLIMITED: TrackRecorderExternalSynthNormalUnlimited,
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
            RecordTypeEnum.AUDIO_ONLY,
            RecordTypeEnum.AUDIO_ONLY_EXPORT,
            RecordTypeEnum.AUDIO_ONLY_EXPORT_ONE,
            RecordTypeEnum.AUDIO_ONLY_MULTI,
        )
