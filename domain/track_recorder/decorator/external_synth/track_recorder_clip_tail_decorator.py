from functools import partial

from typing import Optional

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.track_recorder.decorator.external_synth.AudioClipSilentEvent import AudioClipSilentEvent
from protocol0.domain.track_recorder.decorator.track_recorder_decorator import TrackRecorderDecorator
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderClipTailDecorator(TrackRecorderDecorator, UseFrameworkEvents):
    @property
    def track(self):
        # type: (AbstractTrackRecorder) -> ExternalSynthTrack
        # noinspection PyTypeChecker
        return self._track

    def _on_last_32th_passed_event(self, _):
        # type: (Last32thPassedEvent) -> None
        if self.is_audio_silent:
            DomainEventBus.notify(AudioClipSilentEvent())

    @property
    def is_audio_silent(self):
        # type: () -> bool
        return self.track.audio_tail_track.output_meter_left < 0.1

    def post_audio_record(self):
        # type: () -> Optional[Sequence]
        super(TrackRecorderClipTailDecorator, self).post_audio_record()
        if self.is_audio_silent:
            return None
        else:
            return self._wait_for_clip_tail_end()

    def _wait_for_clip_tail_end(self):
        # type: () -> Sequence
        """ wait for clip tail end and temporarily disable midi input """
        input_routing_type = self.track.midi_track.input_routing.type

        audio_clip = self.track.audio_track.clip_slots[self.recording_scene_index].clip
        audio_clip.fire()
        self.track.midi_track.stop()
        self.track.midi_track.input_routing.type = InputRoutingTypeEnum.NO_INPUT

        DomainEventBus.subscribe(Last32thPassedEvent, self._on_last_32th_passed_event)
        seq = Sequence()
        seq.add(wait_for_event=AudioClipSilentEvent)
        seq.add(partial(setattr, self.track.midi_track.input_routing, "type", input_routing_type))
        seq.add(partial(DomainEventBus.un_subscribe, Last32thPassedEvent, self._on_last_32th_passed_event))
        return seq.done()
