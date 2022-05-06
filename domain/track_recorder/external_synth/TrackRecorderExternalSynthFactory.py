from typing import Optional, Any, cast, Type

from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.AbstractTrackRecorderFactory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.domain.track_recorder.count_in.CountInOneBar import CountInOneBar
from protocol0.domain.track_recorder.count_in.CountInShort import CountInShort
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import \
    TrackRecorderExternalSynthAudio
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioAutomation import \
    TrackRecorderExternalSynthAudioAutomation
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioMulti import \
    TrackRecorderExternalSynthAudioMulti
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioMultiAutomation import \
    TrackRecorderExternalSynthAudioMultiAutomation
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthNormal import \
    TrackRecorderExternalSynthNormal
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthNormalUnlimited import \
    TrackRecorderExternalSynthNormalUnlimited
from protocol0.domain.track_recorder.external_synth.decorator.TrackRecorderClipTailDecorator import \
    TrackRecorderClipTailDecorator
from protocol0.domain.track_recorder.external_synth.decorator.TrackRecorderPropagateNewAudioClipDecorator import \
    TrackRecorderPropagateNewAudioClipDecorator
from protocol0.shared.SongFacade import SongFacade


class TrackRecorderExternalSynthFactory(AbstractTrackRecorderFactory):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthFactory, self).__init__(*a, **k)
        self.track = cast(ExternalSynthTrack, self.track)

    def _get_count_in_class(self, record_type):
        # type: (RecordTypeEnum) -> Type[CountInInterface]
        if record_type in (RecordTypeEnum.NORMAL, RecordTypeEnum.NORMAL_UNLIMITED):
            return CountInOneBar
        else:
            return CountInShort

    def create_recorder(self, record_type):
        # type: (RecordTypeEnum) -> AbstractTrackRecorder
        recorder = super(TrackRecorderExternalSynthFactory, self).create_recorder(record_type)
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder, self._playback_component, self._recording_component)
        elif record_type == RecordTypeEnum.AUDIO_ONLY_AUTOMATION:
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder, self._playback_component, self._recording_component)

        if self.track.audio_tail_track and record_type != RecordTypeEnum.NORMAL_UNLIMITED:
            recorder = TrackRecorderClipTailDecorator(recorder, self._playback_component, self._recording_component)

        return recorder

    def _get_recorder_class(self, record_type):
        # type: (RecordTypeEnum) -> Type[AbstractTrackRecorder]
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            return TrackRecorderExternalSynthAudio
        elif record_type == RecordTypeEnum.AUDIO_ONLY_AUTOMATION:
            return TrackRecorderExternalSynthAudioAutomation
        elif record_type == RecordTypeEnum.AUDIO_ONLY_MULTI:
            return TrackRecorderExternalSynthAudioMulti
        elif record_type == RecordTypeEnum.AUDIO_ONLY_MULTI_AUTOMATION:
            return TrackRecorderExternalSynthAudioMultiAutomation
        elif record_type == RecordTypeEnum.NORMAL:
            return TrackRecorderExternalSynthNormal
        elif record_type == RecordTypeEnum.NORMAL_UNLIMITED:
            return TrackRecorderExternalSynthNormalUnlimited
        else:
            raise Protocol0Error("Unmatched record type %s" % record_type)

    def get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        if record_type in (RecordTypeEnum.NORMAL, RecordTypeEnum.NORMAL_UNLIMITED):
            for i in range(SongFacade.selected_scene().index, len(SongFacade.scenes())):
                if not self.track.midi_track.clip_slots[i].clip and not self.track.audio_track.clip_slots[i].clip:
                    return i

            return None
        else:
            if not self.track.midi_track.clip_slots[SongFacade.selected_scene().index].clip:
                raise Protocol0Warning("No midi clip selected")
            return SongFacade.selected_scene().index

    def get_recording_bar_length(self, record_type):
        # type: (RecordTypeEnum) -> int
        if record_type == RecordTypeEnum.NORMAL:
            return self._recording_bar_length
        elif record_type == RecordTypeEnum.NORMAL_UNLIMITED:
            return 0
        elif record_type in (RecordTypeEnum.AUDIO_ONLY, RecordTypeEnum.AUDIO_ONLY_AUTOMATION):
            midi_clip = self.track.midi_track.clip_slots[SongFacade.selected_scene().index].clip
            return midi_clip.loop.bar_length
        elif record_type in (RecordTypeEnum.AUDIO_ONLY_MULTI, RecordTypeEnum.AUDIO_ONLY_MULTI_AUTOMATION):
            return SongFacade.selected_scene().bar_length
        else:
            raise Protocol0Warning("Unmatched record type %s" % record_type)
