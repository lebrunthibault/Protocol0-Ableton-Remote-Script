from functools import partial

from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.sequence.Sequence import Sequence
from protocol0.track_recorder.decorator.external_synth.abstract_track_recorder_external_synth_decorator import \
    AbstractTrackRecorderExternalSynthDecorator
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.utils.decorators import p0_subject_slot


class TrackRecorderClipTailDecorator(AbstractTrackRecorderExternalSynthDecorator):
    __subject_events__ = ("is_silent",)

    def __init__(self, recorder):
        # type: (AbstractTrackRecorder) -> None
        super(AbstractTrackRecorderExternalSynthDecorator, self).__init__(recorder=recorder)
        self._is_silent_listener.subject = self

    @p0_subject_slot("beat_changed")
    def _beat_changed_listener(self):
        # type: () -> None
        if self.track.audio_tail_track.output_meter_left < 0.1:
            # noinspection PyUnresolvedReferences
            self.notify_is_silent()

    @p0_subject_slot("is_silent")
    def _is_silent_listener(self):
        # type: () -> None
        self.parent.log_dev("tail is silent !")
        pass

    def post_audio_record(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(TrackRecorderClipTailDecorator, self).post_audio_record)
        seq.add(self._wait_for_clip_tail_end)
        return seq.done()

    def _wait_for_clip_tail_end(self):
        # type: () -> Sequence
        self.parent.log_dev("waiting for tail")
        input_routing_type = self.track.midi_track.input_routing_type

        self.track.midi_track.input_routing_type = InputRoutingTypeEnum.NO_INPUT
        self.track.midi_track.stop()
        self.track.audio_track.clip_slots[self.recording_scene_index].clip.fire()
        self._beat_changed_listener.subject = self.parent.beatScheduler

        seq = Sequence()
        seq.add(complete_on=self._is_silent_listener, no_timeout=True)
        seq.add(partial(setattr, self.track.midi_track, "input_routing_type", input_routing_type))
        seq.add(partial(setattr, self._beat_changed_listener, "subject", None))
        return seq.done()
