from typing import Type, Dict, Any

import Live
from _Framework.ControlSurface import ControlSurface
from protocol0.application.ErrorService import ErrorService
from protocol0.application.control_surface.ActionGroupFactory import ActionGroupFactory
from protocol0.application.vocal_command.KeywordSearchService import KeywordSearchService
from protocol0.application.vocal_command.VocalCommandService import VocalCommandService
from protocol0.domain.audit.AudioLatencyAnalyzerService import AudioLatencyAnalyzerService
from protocol0.domain.audit.LogService import LogService
from protocol0.domain.audit.SetFixerService import SetFixerService
from protocol0.domain.audit.SetUpgradeService import SetUpgradeService
from protocol0.domain.audit.SongStatsService import SongStatsService
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import InstrumentPresetScrollerService
from protocol0.domain.lom.instrument.preset.PresetService import PresetService
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.scene.ScenesService import ScenesService
from protocol0.domain.lom.song.SongService import SongService
from protocol0.domain.lom.track.TracksService import SongTracksService
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackService import SimpleDummyTrackService
from protocol0.domain.lom.validation.ValidatorFactory import ValidatorFactory
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.application.CommandBus import CommandBus
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.TrackRecorderService import TrackRecorderService
from protocol0.infra.interface.BrowserLoaderService import BrowserLoaderService
from protocol0.infra.interface.BrowserService import BrowserService
from protocol0.infra.interface.InterfaceClicksService import InterfaceClicksService
from protocol0.infra.midi.MidiService import MidiService
from protocol0.infra.interface.SessionService import SessionService
from protocol0.infra.persistence.SongDataService import SongDataService
from protocol0.infra.logging.LoggerService import LoggerService
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.TickScheduler import TickScheduler
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.shared.SongViewFacade import SongViewFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.types import T


class Container(ContainerInterface):
    """ Direct DI container """

    def __init__(self, control_surface):
        # type: (ControlSurface) -> None
        self._registry = {}  # type: Dict[Type, Any]

        live_song = control_surface.song()  # type: Live.Song.Song
        Logger(LoggerService())
        UndoFacade(live_song.begin_undo_step, live_song.end_undo_step)
        StatusBar(control_surface.show_message)
        Backend(control_surface._send_midi)
        ErrorService()
        midi_service = MidiService(control_surface._send_midi)
        beat_scheduler = BeatScheduler(live_song)
        tick_scheduler = TickScheduler(beat_scheduler, live_song)
        Scheduler(tick_scheduler, beat_scheduler)  # setup Scheduler facade

        song = Song(live_song)
        CommandBus(self, song)

        session_service = SessionService(control_surface.component_guard,
                                         control_surface.set_highlighting_session_component)
        ApplicationView(control_surface.application().view, session_service)

        browser = control_surface.application().browser
        browser_service = BrowserService(browser, BrowserLoaderService(browser))
        device_service = DeviceService(browser_service, song.select_device)
        track_factory = TrackFactory(song)
        SimpleDummyTrackService(browser_service)
        song_tracks_service = SongTracksService(track_factory, song)
        track_recorder_service = TrackRecorderService(song)
        scenes_service = ScenesService(song, track_recorder_service)
        SongFacade(song, song_tracks_service, scenes_service, track_recorder_service)
        SongViewFacade(song)

        song_service = SongService(song)
        Backend.client().end_measurement()
        instrument_display_service = InstrumentDisplayService(device_service)
        instrument_preset_scroller_service = InstrumentPresetScrollerService()
        mixing_service = MixingService(live_song.master_track)
        validator_service = ValidatorService(ValidatorFactory(browser_service))
        set_upgrade_service = SetUpgradeService(device_service, validator_service)
        log_service = LogService()
        set_fixer_service = SetFixerService(
            validator_service=validator_service,
            set_upgrade_service=set_upgrade_service,
            song=song
        )
        song_stats_service = SongStatsService()
        interface_clicks_service = InterfaceClicksService()
        audio_latency_service = AudioLatencyAnalyzerService(track_recorder_service, song,
                                                            interface_clicks_service)
        preset_service = PresetService()
        session_to_arrangement_service = SessionToArrangementService(song)
        song_data_service = SongDataService(live_song.get_data, live_song.set_data)

        # vocal command
        keyword_search_service = KeywordSearchService()
        vocal_command_service = VocalCommandService(keyword_search_service)

        # registering managers in container
        self._register(midi_service)
        self._register(browser_service)
        self._register(song_tracks_service)
        self._register(scenes_service)
        self._register(song_data_service)
        self._register(song_service)
        self._register(instrument_display_service)
        self._register(instrument_preset_scroller_service)
        self._register(mixing_service)
        self._register(track_recorder_service)
        self._register(validator_service)
        self._register(set_upgrade_service)
        self._register(log_service)
        self._register(set_fixer_service)
        self._register(song_stats_service)
        self._register(audio_latency_service)
        self._register(preset_service)
        self._register(session_to_arrangement_service)
        self._register(keyword_search_service)
        self._register(vocal_command_service)

        ActionGroupFactory.create_action_groups(self, song, control_surface.component_guard)

    def _register(self, service):
        # type: (object) -> None

        if service.__class__ in self._registry:
            raise Protocol0Error("service already registered in container : %s" % service)
        self._registry[service.__class__] = service

        base_class = service.__class__.__base__
        if base_class.__name__.endswith("Interface"):
            if base_class in self._registry:
                raise Protocol0Error("interface already registered in container : %s" % base_class)
            self._registry[base_class] = service

    def get(self, cls):
        # type: (Type[T]) -> T
        if cls not in self._registry:
            raise Protocol0Error("Couldn't find %s in container" % cls)

        return self._registry[cls]
