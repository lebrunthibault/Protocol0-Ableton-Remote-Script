from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.domain.track_recorder.count_in.count_in_one_bar import CountInOneBar
from protocol0.domain.track_recorder.count_in.count_in_short import CountInShort
from protocol0.domain.track_recorder.decorator.external_synth.track_recorder_clip_tail_decorator import \
    TrackRecorderClipTailDecorator
from protocol0.domain.track_recorder.decorator.external_synth.track_recorder_propagate_new_audio_clip_decorator import \
    TrackRecorderPropagateNewAudioClipDecorator
from protocol0.domain.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.recorder.track_recorder_external_synth import TrackRecorderExternalSynth
from protocol0.domain.track_recorder.recorder.track_recorder_external_synth_audio import TrackRecorderExternalSynthAudio
from protocol0.shared.InterfaceState import InterfaceState
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackRecorderExternalSynthFactory(AbstractTrackRecorderFactory):
    def __init__(self, track, song):
        # type: (ExternalSynthTrack, Song) -> None
        super(TrackRecorderExternalSynthFactory, self).__init__()
        self.track = track
        self._song = song

    def create_count_in(self, record_type):
        # type: (RecordTypeEnum) -> CountInInterface
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            return CountInShort(self.track, self._song)
        else:
            return CountInOneBar(self.track, self._song)

    def _create_recorder(self, record_type, bar_length):
        # type: (RecordTypeEnum, int) -> AbstractTrackRecorder
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            recorder = TrackRecorderExternalSynthAudio(self.track, self._song)  # type: AbstractTrackRecorder
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder, self._song)
        else:
            recorder = TrackRecorderExternalSynth(self.track, self._song)

        if self.track.audio_tail_track and self.track.record_clip_tails and bar_length != 0:
            recorder = TrackRecorderClipTailDecorator(recorder, self._song)

        return recorder

    def _get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            if not self.track.midi_track.clip_slots[SongFacade.selected_scene().index].clip:
                raise Protocol0Warning("No midi clip selected")
            return SongFacade.selected_scene().index
        else:
            for i in range(SongFacade.selected_scene().index, len(SongFacade.scenes())):
                if not self.track.midi_track.clip_slots[i].clip and not self.track.audio_track.clip_slots[i].clip:
                    return i

            return None

    def get_recording_bar_length(self, record_type):
        # type: (RecordTypeEnum) -> int
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            midi_clip = self.track.midi_track.clip_slots[SongFacade.selected_scene().index].clip
            return midi_clip.bar_length
        else:
            return InterfaceState.SELECTED_RECORDING_BAR_LENGTH.bar_length_value
