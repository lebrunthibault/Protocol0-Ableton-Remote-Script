from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.recorder.decorators.external_synth.track_recorder_propagate_new_audio_clip_decorator import \
    TrackRecorderPropagateNewAudioClipDecorator
from protocol0.recorder.decorators.external_synth.track_recorder_stop_midi_input_decorator import \
    TrackRecorderStopMidiInputDecorator
from protocol0.recorder.decorators.track_recorder_count_in_one_bar_decorator import TrackRecorderCountInOneBarDecorator
from protocol0.recorder.decorators.track_recorder_count_in_short_decorator import TrackRecorderCountInShortDecorator
from protocol0.recorder.decorators.track_recorder_focus_empty_clip_slot_decorator import \
    TrackRecorderFocusEmptyClipSlotDecorator
from protocol0.recorder.track_recorder_external_synth import TrackRecorderExternalSynth
from protocol0.recorder.track_recorder_external_synth_audio import TrackRecorderExternalSynthAudio
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface
from protocol0.recorder.track_recorder_simple import TrackRecorderSimple


class TrackRecorderFactory(AbstractObject):
    @classmethod
    def create_recorder(cls, track, record_type, bar_length):
        # type: (AbstractTrack, RecordTypeEnum, BarLengthEnum) -> TrackRecorderInterface
        recorder = None
        if isinstance(track, SimpleTrack):
            recorder = TrackRecorderSimple(track)
        elif isinstance(track, ExternalSynthTrack):
            if record_type == RecordTypeEnum.NORMAL:
                recorder = TrackRecorderExternalSynth(track)
            elif record_type == RecordTypeEnum.AUDIO_ONLY:
                recorder = TrackRecorderExternalSynthAudio(track)
                recorder = TrackRecorderPropagateNewAudioClipDecorator(recorder)

            if bar_length != BarLengthEnum.UNLIMITED:
                recorder = TrackRecorderStopMidiInputDecorator(recorder)

        if recorder is None:
            raise Protocol0Error("Couldn't generate recorder")

        # apply common decorators
        if record_type == RecordTypeEnum.NORMAL:
            recorder = TrackRecorderFocusEmptyClipSlotDecorator(recorder)
            recorder = TrackRecorderCountInOneBarDecorator(recorder)
        else:
            recorder = TrackRecorderCountInShortDecorator(recorder)

        return recorder
