from functools import partial

from typing import Optional

from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.TrackRecorderDecorator import TrackRecorderDecorator
from protocol0.domain.track_recorder.external_synth.decorator.AudioClipSilentEvent import (
    AudioClipSilentEvent,
)
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderClipTailDecorator(TrackRecorderDecorator):
    # NB : Represents the smoothed momentary peak value of left channel output meter
    # This value is not zero just after the sound is finished
    # and this thus not precise for sounds with a low release
    # But if it were higher we would lose tail ends of sounds with a high release ..
    OUTPUT_METER_LEFT_THRESHOLD = 0.25

    @property
    def track(self):
        # type: (AbstractTrackRecorder) -> ExternalSynthTrack
        # noinspection PyTypeChecker
        return self._track

    def _on_last_32th_passed_event(self, _):
        # type: (Last32thPassedEvent) -> None
        if self.is_audio_silent:
            DomainEventBus.emit(AudioClipSilentEvent())

    @property
    def is_audio_silent(self):
        # type: () -> bool
        return self.track.audio_track.output_meter_left < self.OUTPUT_METER_LEFT_THRESHOLD

    def post_audio_record(self):
        # type: () -> Optional[Sequence]
        super(TrackRecorderClipTailDecorator, self).post_audio_record()

        if self.is_audio_silent:
            midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
            if midi_clip.starts_at_1:
                # Here not waiting will sometimes create a glitch at the very end of the audio clip
                # if the midi clip starts at 1.1.1
                # unfortunately we cannot play the scene right after
                seq = Sequence()
                seq.add(self.track.stop)
                seq.wait_bars(1)
                seq.wait_ms(50)
                return seq.done()
            else:
                return None
        else:
            return self._wait_for_tail_clip_end()

    def _wait_for_tail_clip_end(self):
        # type: () -> Optional[Sequence]
        """wait for clip tail end and temporarily disable midi input"""
        input_routing_type = self.track.midi_track.input_routing.type

        audio_clip = self.track.audio_track.clip_slots[self.recording_scene_index].clip

        if audio_clip is None:
            return None

        audio_clip.loop.looping = False
        audio_tail_clip = None
        if self.track.audio_tail_track is not None:
            audio_tail_clip = self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip

        self.track.midi_track.stop()
        self.track.midi_track.input_routing.type = InputRoutingTypeEnum.COMPUTER_KEYBOARD

        DomainEventBus.subscribe(Last32thPassedEvent, self._on_last_32th_passed_event)
        seq = Sequence()
        seq.wait_for_event(AudioClipSilentEvent, continue_on_song_stop=True)
        seq.log("clip silent !")
        seq.add(partial(audio_clip.stop, immediate=True))  # don't catch end bar glitch
        if audio_tail_clip is not None:
            seq.add(partial(audio_tail_clip.stop, immediate=True))  # idem
        seq.defer()
        # idem
        seq.add(partial(setattr, self.track.midi_track.input_routing, "type", input_routing_type))
        seq.add(
            partial(
                DomainEventBus.un_subscribe, Last32thPassedEvent, self._on_last_32th_passed_event
            )
        )
        return seq.done()
