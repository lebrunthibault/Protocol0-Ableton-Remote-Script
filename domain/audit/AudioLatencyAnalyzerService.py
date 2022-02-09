from functools import partial

from typing import Optional, cast

from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import PresetProgramSelectedEvent
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.InterfaceClicksServiceInterface import InterfaceClicksServiceInterface
from protocol0.domain.shared.System import System
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.TrackRecorderService import TrackRecorderService
from protocol0.shared.SongFacade import SongFacade


class AudioLatencyAnalyzerService(object):
    def __init__(self, track_recorder_service, song, interface_clicks_service):
        # type: (TrackRecorderService, Song, InterfaceClicksServiceInterface) -> None
        self._track_recorder_service = track_recorder_service
        self._song = song
        self._interface_clicks_service = interface_clicks_service

    def test_audio_latency(self):
        # type: () -> Optional[Sequence]
        if SongFacade.usamo_track() is None:
            raise Protocol0Warning("Missing usamo track")

        ext_synth_track = SongFacade.current_track()
        if not isinstance(ext_synth_track, ExternalSynthTrack):
            ext_synth_track = next(SongFacade.prophet_tracks(), None)

        if ext_synth_track is None:
            raise Protocol0Warning("Please select an ExternalSynthTrack")

        tempo = SongFacade.tempo()
        self._song.tempo = 120  # easier to see jitter

        seq = Sequence()
        seq.add(ext_synth_track.duplicate)
        seq.add(self._set_up_track_for_record)
        seq.add(self._create_audio_test_clip)
        seq.add(self._record_test_clip)
        seq.add(self._analyze_jitter)
        seq.add(partial(setattr, self._song, "tempo", tempo))
        return seq.done()

    def _set_up_track_for_record(self):
        # type: () -> None
        current_track = cast(ExternalSynthTrack, SongFacade.current_track())
        # switching to test preset
        DomainEventBus.notify(PresetProgramSelectedEvent(127))
        current_track.record_clip_tails = False

    def _create_audio_test_clip(self):
        # type: () -> Sequence
        current_track = cast(ExternalSynthTrack, SongFacade.current_track())
        # switching to test preset
        seq = Sequence()
        seq.add(current_track.midi_track.clip_slots[0].create_clip)
        seq.add(self._generate_test_notes)
        return seq.done()

    def _generate_test_notes(self):
        # type: () -> Sequence
        current_track = cast(ExternalSynthTrack, SongFacade.current_track())
        pitch = 84
        if isinstance(current_track.instrument, InstrumentMinitaur):
            pitch += 24
        notes = [Note(pitch=pitch, velocity=127, start=float(i) / 2, duration=0.25) for i in range(0, 8)]

        seq = Sequence()
        seq.add(partial(current_track.midi_track.clips[0].set_notes, notes))
        return seq.done()

    def _record_test_clip(self):
        # type: () -> Sequence
        current_track = cast(ExternalSynthTrack, SongFacade.current_track())
        seq = Sequence()
        seq.add(partial(setattr, current_track, "mute", True))
        seq.add(partial(self._track_recorder_service.record_track, current_track,
                        RecordTypeEnum.AUDIO_ONLY))
        seq.add(lambda: current_track.audio_track.clips[0].select())
        seq.add(wait=10)
        return seq.done()

    def _analyze_jitter(self):
        # type: () -> Sequence
        current_track = cast(ExternalSynthTrack, SongFacade.current_track())
        audio_clip = current_track.audio_track.clips[0]
        seq = Sequence()
        seq.add(partial(audio_clip.quantize, depth=0))
        seq.add(self._interface_clicks_service.save_sample)
        seq.add(partial(System.client().analyze_test_audio_clip_jitter, clip_path=audio_clip.file_path),
                wait_for_system=True)
        seq.add(current_track.delete)
        return seq.done()
