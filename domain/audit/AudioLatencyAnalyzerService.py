from functools import partial

from typing import Optional

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ResetPlaybackCommand import ResetPlaybackCommand
from protocol0.domain.lom.instrument.InstrumentActivatedEvent import InstrumentActivatedEvent
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import (
    PresetProgramSelectedEvent,
)
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.shared.InterfaceClicksServiceInterface import InterfaceClicksServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class AudioLatencyAnalyzerService(object):
    def __init__(
        self,
        track_recorder_service,
        interface_clicks_service,
        track_crud_component,
        tempo_component,
    ):
        # type: (RecordService, InterfaceClicksServiceInterface, TrackCrudComponent, TempoComponent) -> None
        self._track_recorder_service = track_recorder_service
        self._interface_clicks_service = interface_clicks_service
        self._track_crud_component = track_crud_component
        self._tempo_component = tempo_component

    def test_audio_latency(self, track):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        tempo = Song.tempo()
        self._tempo_component.tempo = 120  # easier to see jitter

        seq = Sequence()
        seq.add(partial(self._track_crud_component.duplicate_track, track))
        if track.instrument.needs_exclusive_activation:
            seq.wait_for_event(InstrumentActivatedEvent)
        seq.add(self._set_up_track_for_record)
        seq.add(self._create_audio_test_clip)
        seq.add(self._record_test_clip)
        seq.add(self._analyze_jitter)
        seq.add(partial(setattr, self._tempo_component, "tempo", tempo))
        return seq.done()

    def _set_up_track_for_record(self):
        # type: () -> None
        track = Song.current_external_synth_track()

        track.name = "Test USAMO"

        # we need this here but not in InstrumentInterface for some reason
        track.midi_track.input_routing.type = InputRoutingTypeEnum.ALL_INS
        # switching to test preset (last)
        DomainEventBus.emit(PresetProgramSelectedEvent(127))
        # Scheduler.defer(partial(track.instrument.preset_list.load_preset, track.instrument.preset_list.presets[-1]))

    def _create_audio_test_clip(self):
        # type: () -> Sequence
        track = Song.current_external_synth_track()
        # switching to test preset
        seq = Sequence()
        seq.add(track.midi_track.clip_slots[0].create_clip)
        seq.add(self._generate_test_notes)
        return seq.done()

    def _generate_test_notes(self):
        # type: () -> Sequence
        track = Song.current_external_synth_track()
        pitch = 84
        if isinstance(track.instrument, InstrumentMinitaur):
            pitch += 24
        notes = [
            Note(pitch=pitch, velocity=127, start=float(i) / 2, duration=0.25) for i in range(0, 8)
        ]

        seq = Sequence()
        seq.add(partial(track.midi_track.clips[0].set_notes, notes))
        return seq.done()

    def _record_test_clip(self):
        # type: () -> Sequence
        track = Song.current_external_synth_track()
        seq = Sequence()
        seq.add(
            partial(self._track_recorder_service.record_track, track, RecordTypeEnum.AUDIO)
        )
        seq.add(
            lambda: track.audio_track.clip_slots[0].select()
        )
        seq.add(partial(CommandBus.dispatch, ResetPlaybackCommand()))
        seq.wait(10)
        return seq.done()

    def _analyze_jitter(self):
        # type: () -> Sequence
        track = Song.current_external_synth_track()
        audio_clip = track.audio_track.clips[0]
        seq = Sequence()
        seq.add(partial(audio_clip.quantize, depth=0))
        seq.add(self._interface_clicks_service.save_sample)
        seq.add(
            partial(Backend.client().analyze_test_audio_clip_jitter, clip_path=audio_clip.file_path)
        )
        return seq.done()
