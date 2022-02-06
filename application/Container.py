from _Framework.ControlSurface import ControlSurface
from protocol0.application.faderfox.ActionGroupFactory import ActionGroupFactory
from protocol0.application.interface.ClickManager import ClickManager
from protocol0.application.interface.SessionManager import SessionManager
from protocol0.application.service.ErrorManager import ErrorManager
from protocol0.application.service.LogManager import LogManager
from protocol0.application.vocal_command.KeywordSearchManager import KeywordSearchManager
from protocol0.application.vocal_command.VocalCommandManager import VocalCommandManager
from protocol0.domain.CommandBus import CommandBus
from protocol0.domain.audit.AudioLatencyAnalyzer import AudioLatencyAnalyzer
from protocol0.domain.audit.SetFixerManager import SetFixerManager
from protocol0.domain.audit.SetUpgradeManager import SetUpgradeManager
from protocol0.domain.audit.SongStatsManager import SongStatsManager
from protocol0.domain.lom.automation.AutomationTrackManager import AutomationTrackManager
from protocol0.domain.lom.device.DeviceManager import DeviceManager
from protocol0.domain.lom.instrument.InstrumentDisplayManager import InstrumentDisplayManager
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerManager import InstrumentPresetScrollerManager
from protocol0.domain.lom.instrument.preset.PresetManager import PresetManager
from protocol0.domain.lom.scene.SongScenesManager import SongScenesManager
from protocol0.domain.lom.set.MixingManager import MixingManager
from protocol0.domain.lom.set.SessionToArrangementManager import SessionToArrangementManager
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.song.SongManager import SongManager
from protocol0.domain.lom.song.SongTracksManager import SongTracksManager
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.validation.ValidatorFactory import ValidatorFactory
from protocol0.domain.lom.validation.ValidatorManager import ValidatorManager
from protocol0.domain.track_recorder.track_recorder_manager import TrackRecorderManager
from protocol0.infra.BrowserManager import BrowserManager
from protocol0.infra.MidiManager import MidiManager
from protocol0.infra.SongDataManager import SongDataManager
from protocol0.infra.System import System


class Container(object):
    """ Direct DI container """

    # noinspection PyAttributeOutsideInit
    def build(self, control_surface):
        # type: (ControlSurface) -> None
        # setting up scheduler and midi communication system
        self.midi_manager = MidiManager(CommandBus, control_surface._send_midi)
        self.song = Song(control_surface.song())
        session_manager = SessionManager(control_surface.component_guard, control_surface.set_highlighting_session_component)
        self.song_tracks_manager = SongTracksManager(TrackFactory(), session_manager, self.song)  # done
        self.song_scenes_manager = SongScenesManager()  # done
        self.song_manager = SongManager(
            song_tracks_manager=self.song_tracks_manager,
            song_scenes_manager=self.song_scenes_manager,
            session_manager=session_manager)  # done
        self.error_manager = ErrorManager(self.song_manager)  # done
        self.song_data_manager = SongDataManager()  # done
        System.get_instance().end_measurement()
        self.browser_manager = BrowserManager()  # done
        self.device_manager = DeviceManager(self.browser_manager)  # done
        self.instrument_display_manager = InstrumentDisplayManager(self.device_manager)  # done
        self.instrument_preset_scroller_manager = InstrumentPresetScrollerManager()  # done
        self.mixing_manager = MixingManager()  # done
        self.track_recorder_manager = TrackRecorderManager()  # done
        self.click_manager = ClickManager()  # done
        self.automation_track_manager = AutomationTrackManager(self.click_manager)  # done
        self.validator_manager = ValidatorManager(ValidatorFactory())  # done
        self.set_upgrade_manager = SetUpgradeManager(self.device_manager, self.validator_manager)  # done
        self.log_manager = LogManager()  # done
        self.set_fixer_manager = SetFixerManager(
            validator_manager=self.validator_manager,
            set_upgrade_manager=self.set_upgrade_manager,
        )  # done
        self.song_stats_manager = SongStatsManager()  # done
        self.audio_latency_manager = AudioLatencyAnalyzer(self.track_recorder_manager, self.click_manager)  # done
        self.preset_manager = PresetManager()  # done
        self.session_to_arrangement_manager = SessionToArrangementManager()  # done

        # action groups
        ActionGroupFactory.create_action_groups(self)  # done

        # vocal command
        self.keyword_search_manager = KeywordSearchManager()  # done
        self.vocal_command_manager = VocalCommandManager(self.keyword_search_manager)  # done
