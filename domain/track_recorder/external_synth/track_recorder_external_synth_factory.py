from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.domain.track_recorder.count_in.count_in_one_bar import CountInOneBar
from protocol0.domain.track_recorder.count_in.count_in_short import CountInShort
from protocol0.domain.track_recorder.external_synth.decorator.track_recorder_clip_tail_decorator import \
    TrackRecorderClipTailDecorator
from protocol0.domain.track_recorder.external_synth.decorator.track_recorder_propagate_new_audio_clip_decorator import \
    TrackRecorderPropagateNewAudioClipDecorator
from protocol0.domain.track_recorder.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.external_synth.track_recorder_external_synth import TrackRecorderExternalSynth
from protocol0.domain.track_recorder.external_synth.track_recorder_external_synth_audio import TrackRecorderExternalSynthAudio
from protocol0.domain.track_recorder.external_synth.track_recorder_external_synth_audio_automation import \
    TrackRecorderExternalSynthAudioAutomation
from protocol0.domain.track_recorder.external_synth.track_recorder_external_synth_audio_multi import \
    TrackRecorderExternalSynthAudioMulti
from protocol0.domain.track_recorder.external_synth.track_recorder_external_synth_audio_multi_automation import \
    TrackRecorderExternalSynthAudioMultiAutomation
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackRecorderExternalSynthFactory(AbstractTrackRecorderFactory):
    def __init__(self, track, song, recording_bar_length):
        # type: (ExternalSynthTrack, Song, int) -> None
        super(TrackRecorderExternalSynthFactory, self).__init__()
        self.track = track
        self._song = song
        self._recording_bar_length = recording_bar_length

    def create_count_in(self, record_type):
        # type: (RecordTypeEnum) -> CountInInterface
        if record_type == RecordTypeEnum.NORMAL:
            return CountInOneBar(self.track, self._song)
        else:
            return CountInShort(self.track, self._song)

    def _create_recorder(self, record_type, bar_length):
        # type: (RecordTypeEnum, int) -> AbstractTrackRecorder
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            recorder = TrackRecorderExternalSynthAudio(self.track, self._song)  # type: AbstractTrackRecorder
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder, self._song)
        elif record_type == RecordTypeEnum.AUDIO_ONLY_AUTOMATION:
            recorder = TrackRecorderExternalSynthAudioAutomation(self.track, self._song)
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder, self._song)
        elif record_type == RecordTypeEnum.AUDIO_ONLY_MULTI:
            recorder = TrackRecorderExternalSynthAudioMulti(self.track, self._song)
        elif record_type == RecordTypeEnum.AUDIO_ONLY_MULTI_AUTOMATION:
            recorder = TrackRecorderExternalSynthAudioMultiAutomation(self.track, self._song)
        elif record_type == RecordTypeEnum.NORMAL:
            recorder = TrackRecorderExternalSynth(self.track, self._song)
        else:
            raise Protocol0Warning("Unmatched record type %s" % record_type)

        if self.track.audio_tail_track and bar_length != 0:
            recorder = TrackRecorderClipTailDecorator(recorder, self._song)

        return recorder

    def _get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        if record_type == RecordTypeEnum.NORMAL:
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
        elif record_type in (RecordTypeEnum.AUDIO_ONLY, RecordTypeEnum.AUDIO_ONLY_AUTOMATION):
            midi_clip = self.track.midi_track.clip_slots[SongFacade.selected_scene().index].clip
            return midi_clip.bar_length
        elif record_type in (RecordTypeEnum.AUDIO_ONLY_MULTI, RecordTypeEnum.AUDIO_ONLY_MULTI_AUTOMATION):
            return SongFacade.selected_scene().bar_length
        else:
            raise Protocol0Warning("Unmatched record type %s" % record_type)
