from functools import partial

import Live
from typing import Optional

from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.TrackRecordingStartedEvent import TrackRecordingStartedEvent
from protocol0.shared.Config import Config
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


class QuantizationComponent(object):
    def __init__(self, song, tempo_component):
        # type: (Live.Song.Song, TempoComponent) -> None
        self._song = song
        self._tempo_component = tempo_component
        self._midi_recording_quantization_checked = False  # type: bool
        DomainEventBus.subscribe(TrackRecordingStartedEvent, self._on_track_recording_started_event)

    def _on_track_recording_started_event(self, _):
        # type: (TrackRecordingStartedEvent) -> Optional[Sequence]
        if self._midi_recording_quantization_checked or self.midi_recording_quantization == self.tempo_default_midi_recording_quantization:
            return None

        self._midi_recording_quantization_checked = True
        seq = Sequence()
        seq.prompt("Midi recording quantization %s is not tempo default : %s, Set to default ?" % (
            self.midi_recording_quantization, self.tempo_default_midi_recording_quantization))
        seq.add(
            partial(setattr, self, "midi_recording_quantization", self.tempo_default_midi_recording_quantization))
        seq.add(partial(StatusBar.show_message,
                        "Quantization set to %s" % self.tempo_default_midi_recording_quantization))

        return seq.done()

    @property
    def midi_recording_quantization(self):
        # type: () -> int
        return self._song.midi_recording_quantization

    @midi_recording_quantization.setter
    def midi_recording_quantization(self, midi_recording_quantization):
        # type: (int) -> None
        if self._song:
            self._song.midi_recording_quantization = midi_recording_quantization

    @property
    def clip_trigger_quantization(self):
        # type: () -> int
        return self._song.clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, clip_trigger_quantization):
        # type: (int) -> None
        self._song.clip_trigger_quantization = clip_trigger_quantization

    @property
    def tempo_default_midi_recording_quantization(self):
        # type: () -> property
        """We adapt the global quantization depending on the tempo"""
        if self._tempo_component.tempo < Config.SPLIT_QUANTIZATION_TEMPO:
            return Live.Song.RecordingQuantization.rec_q_sixtenth
        else:
            return Live.Song.RecordingQuantization.rec_q_eight
