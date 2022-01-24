from typing import Optional

from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.errors.Protocol0Warning import Protocol0Warning
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.track_recorder.decorator.external_synth.track_recorder_clip_tail_decorator import \
    TrackRecorderClipTailDecorator
from protocol0.track_recorder.decorator.external_synth.track_recorder_propagate_new_audio_clip_decorator import \
    TrackRecorderPropagateNewAudioClipDecorator
from protocol0.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.track_recorder.recorder.track_recorder_external_synth import TrackRecorderExternalSynth
from protocol0.track_recorder.recorder.track_recorder_external_synth_audio import TrackRecorderExternalSynthAudio


class TrackRecorderExternalSynthFactory(AbstractTrackRecorderFactory):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        super(TrackRecorderExternalSynthFactory, self).__init__()
        self.track = track

    def _create_recorder(self, record_type, bar_length):
        # type: (RecordTypeEnum, int) -> AbstractTrackRecorder
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            recorder = TrackRecorderExternalSynthAudio(self.track)
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder)
        else:
            recorder = TrackRecorderExternalSynth(self.track)

        if self.track.audio_tail_track and self.track.record_clip_tails and bar_length != 0:
            recorder = TrackRecorderClipTailDecorator(recorder)

        return recorder

    def _get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            if not self.track.midi_track.clip_slots[self.song.selected_scene.index].clip:
                raise Protocol0Warning("No midi clip selected")
            return self.song.selected_scene.index
        else:
            for i in range(self.song.selected_scene.index, len(self.song.scenes)):
                if not self.track.midi_track.clip_slots[i].clip and not self.track.audio_track.clip_slots[i].clip:
                    return i

            return None

    def get_recording_bar_length(self, record_type):
        # type: (RecordTypeEnum) -> int
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            midi_clip = self.track.midi_track.clip_slots[self.song.selected_scene.index].clip
            return midi_clip.bar_length
        else:
            return InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value
