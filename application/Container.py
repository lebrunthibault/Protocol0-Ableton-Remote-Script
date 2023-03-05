import Live
from _Framework.ControlSurface import ControlSurface
from typing import Type, Dict, Any

from protocol0.application.CommandBus import CommandBus
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.control_surface.ActionGroupFactory import ActionGroupFactory
from protocol0.application.error.ErrorService import ErrorService
from protocol0.application.error.SentryService import SentryService
from protocol0.domain.audit.AudioLatencyAnalyzerService import AudioLatencyAnalyzerService
from protocol0.domain.audit.LogService import LogService
from protocol0.domain.audit.SetFixerService import SetFixerService
from protocol0.domain.audit.SetProfilingService import SetProfilingService
from protocol0.domain.audit.SetUpgradeService import SetUpgradeService
from protocol0.domain.audit.SongStatsService import SongStatsService
from protocol0.domain.lom.device.DeviceDisplayService import DeviceDisplayService
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.device.DrumRackService import DrumRackService
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import (
    InstrumentPresetScrollerService,
)
from protocol0.domain.lom.instrument.preset.PresetService import PresetService
from protocol0.domain.lom.scene.PlayingSceneFacade import PlayingSceneFacade
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.domain.lom.song.SongInitService import SongInitService
from protocol0.domain.lom.song.components.ClipComponent import ClipComponent
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.QuantizationComponent import QuantizationComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.TrackAutomationService import TrackAutomationService
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.domain.lom.track.TrackService import TrackService
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackService import \
    MatchingTrackService
from protocol0.domain.lom.track.simple_track.SimpleTrackService import SimpleTrackService
from protocol0.domain.lom.validation.ValidatorFactory import ValidatorFactory
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.infra.interface.BrowserLoaderService import BrowserLoaderService
from protocol0.infra.interface.BrowserService import BrowserService
from protocol0.infra.interface.InterfaceClicksService import InterfaceClicksService
from protocol0.infra.interface.session.SessionService import SessionService
from protocol0.infra.logging.LoggerService import LoggerService
from protocol0.infra.midi.MidiService import MidiService
from protocol0.infra.persistence.SongDataService import SongDataService
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.TickScheduler import TickScheduler
from protocol0.shared.Song import Song
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.types import T


class Container(ContainerInterface):
    """Direct DI container"""

    def __init__(self, control_surface):
        # type: (ControlSurface) -> None
        self._registry = {}  # type: Dict[Type, Any]

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

        live_song = control_surface.song()  # type: Live.Song.Song

        Logger(LoggerService())
        UndoFacade(live_song.begin_undo_step, live_song.end_undo_step)
        StatusBar(control_surface.show_message)
        Backend(control_surface._send_midi)
        ErrorService(SentryService(), live_song)
        midi_service = MidiService(control_surface._send_midi)
        beat_scheduler = BeatScheduler(live_song)
        tick_scheduler = TickScheduler(beat_scheduler, live_song)
        Scheduler(tick_scheduler, beat_scheduler)  # setup Scheduler facade

        # song components
        clip_component = ClipComponent(live_song.view)
        device_component = DeviceComponent(live_song.view)
        playback_component = PlaybackComponent(live_song)
        tempo_component = TempoComponent(live_song)
        quantization_component = QuantizationComponent(live_song, tempo_component)
        recording_component = RecordingComponent(live_song)
        scene_component = SceneComponent(live_song.view)
        scene_crud_component = SceneCrudComponent(
            live_song.create_scene, live_song.duplicate_scene, live_song.delete_scene
        )
        track_component = TrackComponent(live_song.view)
        track_crud_component = TrackCrudComponent(
            live_song.create_midi_track,
            live_song.create_audio_track,
            live_song.duplicate_track,
            live_song.delete_track,
        )

        ableton_set = AbletonSet()

        CommandBus(self, ableton_set)

        session_service = SessionService(
            control_surface.component_guard, control_surface.set_highlighting_session_component
        )
        ApplicationView(
            recording_component, control_surface.application().view, session_service
        )

        browser = control_surface.application().browser
        browser_service = BrowserService(browser, BrowserLoaderService(browser))
        device_display_service = DeviceDisplayService(browser_service)
        instrument_display_service = InstrumentDisplayService(device_display_service)
        device_service = DeviceService(track_crud_component, device_component, browser_service)
        drum_rack_service = DrumRackService(browser_service)
        track_factory = TrackFactory(track_crud_component, browser_service, drum_rack_service)
        track_automation_service = TrackAutomationService(track_factory)
        track_mapper_service = TrackMapperService(live_song, track_factory)
        track_service = TrackService()
        track_recorder_service = RecordService(
            playback_component,
            scene_crud_component,
            quantization_component,
        )
        SimpleTrackService()
        matching_track_service = MatchingTrackService(track_crud_component)
        scene_service = SceneService(live_song, scene_crud_component)
        scene_playback_service = ScenePlaybackService(playback_component)
        PlayingSceneFacade(scene_component)
        validator_service = ValidatorService(ValidatorFactory(browser_service))
        set_upgrade_service = SetUpgradeService(validator_service, track_crud_component)
        set_fixer_service = SetFixerService(
            validator_service=validator_service,
            set_upgrade_service=set_upgrade_service,
        )
        session_to_arrangement_service = SessionToArrangementService(
            playback_component,
            recording_component,
            quantization_component,
            scene_component,
            tempo_component,
            track_component,
            set_fixer_service,
        )
        Song(
            live_song,
            clip_component,
            device_component,
            playback_component,
            quantization_component,
            recording_component,
            scene_component,
            tempo_component,
            track_component,
            scene_service,
            track_mapper_service,
            track_recorder_service,
            session_to_arrangement_service,
        )

        song_service = SongInitService(playback_component, ableton_set)
        instrument_preset_scroller_service = InstrumentPresetScrollerService()
        mixing_service = MixingService()
        interface_clicks_service = InterfaceClicksService()

        # presets
        preset_service = PresetService()

        song_data_service = SongDataService(live_song.get_data, live_song.set_data, scene_component)

        # audit
        audio_latency_service = AudioLatencyAnalyzerService(
            track_recorder_service, interface_clicks_service, track_crud_component, tempo_component
        )
        log_service = LogService(ableton_set, track_mapper_service)

        set_profiling_service = SetProfilingService()
        song_stats_service = SongStatsService()

        self._register(midi_service)
        self._register(browser_service)

        # song components
        self._register(playback_component)
        self._register(scene_component)
        self._register(scene_crud_component)
        self._register(ableton_set)
        self._register(track_component)
        self._register(track_crud_component)
        self._register(tempo_component)

        self._register(song_service)
        self._register(song_data_service)

        self._register(track_factory)
        self._register(track_automation_service)
        self._register(track_mapper_service)
        self._register(track_service)
        self._register(matching_track_service)

        self._register(scene_service)
        self._register(scene_playback_service)

        self._register(instrument_display_service)
        self._register(instrument_preset_scroller_service)

        self._register(device_service)
        self._register(drum_rack_service)

        self._register(mixing_service)
        self._register(track_recorder_service)
        self._register(validator_service)
        self._register(preset_service)

        # audit
        self._register(audio_latency_service)
        self._register(log_service)
        self._register(set_upgrade_service)
        self._register(set_fixer_service)
        self._register(set_profiling_service)
        self._register(song_stats_service)

        self._register(session_to_arrangement_service)

        ActionGroupFactory.create_action_groups(self, control_surface.component_guard)

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

    def _disconnect(self):
        # type: () -> None
        Scheduler.reset()
        self.get(SceneService).disconnect()
        self.get(PlaybackComponent).disconnect()
        self.get(TempoComponent).disconnect()
        self.get(TrackComponent).disconnect()
        self.get(TrackMapperService).disconnect()

        self._registry = {}
