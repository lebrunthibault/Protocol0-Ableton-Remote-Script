from typing import Optional

from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.track_recorder.decorator.external_synth.track_recorder_propagate_new_audio_clip_decorator import \
    TrackRecorderPropagateNewAudioClipDecorator
from protocol0.track_recorder.decorator.external_synth.track_recorder_stop_midi_input_decorator import \
    TrackRecorderStopMidiInputDecorator
from protocol0.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.track_recorder.recorder.track_recorder_external_synth import TrackRecorderExternalSynth
from protocol0.track_recorder.recorder.track_recorder_external_synth_audio import TrackRecorderExternalSynthAudio


class TrackRecorderExternalSynthFactory(AbstractTrackRecorderFactory):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        super(TrackRecorderExternalSynthFactory, self).__init__()
        self.track = track

    def _create_recorder(self, record_type):
        # type: (RecordTypeEnum) -> AbstractTrackRecorder
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            recorder = TrackRecorderExternalSynthAudio(self.track)
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder)
        else:
            recorder = TrackRecorderExternalSynth(self.track)

        recorder = TrackRecorderStopMidiInputDecorator(recorder)

        return recorder

    def _get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        if record_type == RecordTypeEnum.AUDIO_ONLY:
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
            return super(TrackRecorderExternalSynthFactory, self).get_recording_bar_length(record_type)
