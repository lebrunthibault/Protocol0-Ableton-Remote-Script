from typing import Type, Dict, Any

import Live

from _Framework.ControlSurface import ControlSurface
from protocol0.application.faderfox.ActionGroupFactory import ActionGroupFactory
from protocol0.application.ErrorManager import ErrorManager
from protocol0.application.vocal_command.KeywordSearchManager import KeywordSearchManager
from protocol0.application.vocal_command.VocalCommandManager import VocalCommandManager
from protocol0.domain.audit.AudioLatencyAnalyzer import AudioLatencyAnalyzer
from protocol0.domain.audit.SetFixerManager import SetFixerManager
from protocol0.domain.audit.SetUpgradeManager import SetUpgradeManager
from protocol0.domain.audit.SongStatsManager import SongStatsManager
from protocol0.domain.lom.LogManager import LogManager
from protocol0.domain.lom.device.DeviceManager import DeviceManager
from protocol0.domain.lom.instrument.InstrumentDisplayManager import InstrumentDisplayManager
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerManager import InstrumentPresetScrollerManager
from protocol0.domain.lom.instrument.preset.PresetManager import PresetManager
from protocol0.domain.lom.set.MixingManager import MixingManager
from protocol0.domain.lom.set.SessionToArrangementManager import SessionToArrangementManager
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.song.SongManager import SongManager
from protocol0.domain.lom.song.SongScenesManager import SongScenesManager
from protocol0.domain.lom.song.SongTracksManager import SongTracksManager
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackManager import SimpleDummyTrackManager
from protocol0.domain.lom.validation.ValidatorFactory import ValidatorFactory
from protocol0.domain.lom.validation.ValidatorManager import ValidatorManager
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.CommandBus import CommandBus
from protocol0.domain.shared.System import System
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.track_recorder_manager import TrackRecorderManager
from protocol0.infra.BrowserManager import BrowserManager
from protocol0.infra.InterfaceClicksManager import InterfaceClicksManager
from protocol0.infra.MidiManager import MidiManager
from protocol0.infra.SessionManager import SessionManager
from protocol0.infra.SongDataManager import SongDataManager
from protocol0.infra.log import log_ableton
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.FastScheduler import FastScheduler
from protocol0.shared.ContainerInterface import ContainerInterface
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.StatusBar import StatusBar
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.my_types import T


class Container(ContainerInterface):
    """ Direct DI container """

    def __init__(self, control_surface):
        # type: (ControlSurface) -> None
        self._registry = {}  # type: Dict[Type, Any]

        live_song = control_surface.song()  # type: Live.Song.Song

        Logger(log_ableton)
        StatusBar(control_surface.show_message)
        ErrorManager()

        System(control_surface._send_midi)
        UndoFacade(live_song.begin_undo_step, live_song.end_undo_step)
        song = Song(live_song)
        CommandBus(self, song)

        Scheduler(FastScheduler(), BeatScheduler(unschedule_on_stop=True))  # setup Scheduler facade
        midi_manager = MidiManager(control_surface._send_midi)
        session_manager = SessionManager(control_surface.component_guard,
                                         control_surface.set_highlighting_session_component)
        ApplicationView(control_surface.application().view, session_manager)

        browser_manager = BrowserManager()
        device_manager = DeviceManager(browser_manager, song.select_device)
        track_factory = TrackFactory(song)
        SimpleDummyTrackManager(browser_manager)
        song_tracks_manager = SongTracksManager(track_factory, song)
        song_scenes_manager = SongScenesManager(song)
        SongFacade(song, song_tracks_manager, song_scenes_manager)
        song_data_manager = SongDataManager(live_song.get_data, live_song.set_data)
        song_manager = SongManager()
        System.client().end_measurement()
        instrument_display_manager = InstrumentDisplayManager(device_manager)
        instrument_preset_scroller_manager = InstrumentPresetScrollerManager()
        mixing_manager = MixingManager(live_song.master_track)
        track_recorder_manager = TrackRecorderManager(song)
        validator_manager = ValidatorManager(ValidatorFactory(browser_manager))
        set_upgrade_manager = SetUpgradeManager(device_manager, validator_manager)
        log_manager = LogManager()
        set_fixer_manager = SetFixerManager(
            validator_manager=validator_manager,
            set_upgrade_manager=set_upgrade_manager,
            song=song
        )
        song_stats_manager = SongStatsManager()
        interface_clicks_manager = InterfaceClicksManager()
        audio_latency_manager = AudioLatencyAnalyzer(track_recorder_manager, song,
                                                     interface_clicks_manager)
        preset_manager = PresetManager()
        session_to_arrangement_manager = SessionToArrangementManager(song)

        # vocal command
        keyword_search_manager = KeywordSearchManager()
        vocal_command_manager = VocalCommandManager(keyword_search_manager)

        # registering managers in container
        self._register(midi_manager)
        self._register(browser_manager)
        self._register(song_tracks_manager)
        self._register(song_scenes_manager)
        self._register(song_data_manager)
        self._register(song_manager)
        self._register(instrument_display_manager)
        self._register(instrument_preset_scroller_manager)
        self._register(mixing_manager)
        self._register(track_recorder_manager)
        self._register(validator_manager)
        self._register(set_upgrade_manager)
        self._register(log_manager)
        self._register(set_fixer_manager)
        self._register(song_stats_manager)
        self._register(audio_latency_manager)
        self._register(preset_manager)
        self._register(session_to_arrangement_manager)
        self._register(keyword_search_manager)
        self._register(vocal_command_manager)

        ActionGroupFactory.create_action_groups(self, song)

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
