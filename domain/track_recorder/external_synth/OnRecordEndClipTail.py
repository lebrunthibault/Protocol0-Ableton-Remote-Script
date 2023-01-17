from functools import partial

from typing import Optional

from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.external_synth.AudioClipSilentEvent import (
    AudioClipSilentEvent,
)
from protocol0.shared.sequence.Sequence import Sequence


class OnRecordEndClipTail(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> Optional[Sequence]
        if self.is_audio_silent(track):
            midi_clip = track.midi_track.clip_slots[config.scene_index].clip
            if midi_clip.starts_at_1:
                # Here not waiting will sometimes create a glitch at the very end of the audio clip
                # if the midi clip starts at 1.1.1
                # unfortunately we cannot play the scene right after
                seq = Sequence()
                seq.add(track.stop)
                seq.wait_bars(1)
                seq.wait_ms(50)
                return seq.done()
            else:
                return None

        return self._wait_for_tail_clip_end(track, config)

    def is_audio_silent(self, track):
        # type: (ExternalSynthTrack) -> bool
        # NB : Represents the smoothed momentary peak value of left channel output meter
        # This value is not zero just after the sound is finished
        # and this thus not precise for sounds with a low release
        # But if it were higher we would lose tail ends of sounds with a high release ..
        output_meter_left_threshold = 0.25

        return track.audio_track.output_meter_left < output_meter_left_threshold

    def _wait_for_tail_clip_end(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> Optional[Sequence]
        """wait for clip tail end and temporarily disable midi input"""
        audio_clip = track.audio_track.clip_slots[config.scene_index].clip

        if audio_clip is None:
            return None

        audio_clip.loop.looping = False
        track.midi_track.stop()


        def on_last_32th_passed_event(_):
            # type: (Last32thPassedEvent) -> None
            if self.is_audio_silent(track):
                DomainEventBus.emit(AudioClipSilentEvent())
                DomainEventBus.un_subscribe(Last32thPassedEvent, on_last_32th_passed_event)

        DomainEventBus.subscribe(Last32thPassedEvent, on_last_32th_passed_event)
        seq = Sequence()
        seq.wait_for_event(AudioClipSilentEvent, continue_on_song_stop=True)
        seq.add(partial(audio_clip.stop, immediate=True))  # don't catch end bar glitch
        return seq.done()

