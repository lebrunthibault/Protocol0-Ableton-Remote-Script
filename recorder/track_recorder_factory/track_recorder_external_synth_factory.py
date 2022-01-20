from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.recorder.track_recorder_decorator.external_synth.track_recorder_propagate_new_audio_clip_decorator import \
    TrackRecorderPropagateNewAudioClipDecorator
from protocol0.recorder.track_recorder_decorator.external_synth.track_recorder_stop_midi_input_decorator import \
    TrackRecorderStopMidiInputDecorator
from protocol0.recorder.track_recorder_external_synth import TrackRecorderExternalSynth
from protocol0.recorder.track_recorder_external_synth_audio import TrackRecorderExternalSynthAudio
from protocol0.recorder.track_recorder_factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface


class TrackRecorderFactory(AbstractTrackRecorderFactory):
    @classmethod
    def create_recorder(cls, track, record_type, bar_length):
        # type: (ExternalSynthTrack, RecordTypeEnum, BarLengthEnum) -> TrackRecorderInterface
        """ breaking lsp """
        if record_type == RecordTypeEnum.AUDIO_ONLY:
            recorder = TrackRecorderExternalSynthAudio(track)
            recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder)
        else:
            recorder = TrackRecorderExternalSynth(track)

        if bar_length != BarLengthEnum.UNLIMITED:
            recorder = TrackRecorderStopMidiInputDecorator(recorder)

        return recorder
