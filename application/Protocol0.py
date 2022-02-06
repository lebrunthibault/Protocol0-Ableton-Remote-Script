from json import JSONEncoder
from types import MethodType

from ClyphX_Pro import ParseUtils
from typing import Callable, Any, Optional, Union, List

# noinspection PyUnresolvedReferences
from _Framework.ControlSurface import ControlSurface, get_control_surfaces
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
from protocol0.domain.lom.clip.ClipManager import ClipManager
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
from protocol0.domain.lom.validation.ValidatorManager import ValidatorManager
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.SongFacade import SongFacade
from protocol0.domain.shared.utils import find_if
from protocol0.domain.track_recorder.track_recorder_manager import TrackRecorderManager
from protocol0.infra.BrowserManager import BrowserManager
from protocol0.infra.MidiManager import MidiManager
from protocol0.infra.SongDataManager import SongDataManager
from protocol0.infra.System import System
from protocol0.infra.TrackDataManager import TrackDataManager
from protocol0.infra.scheduler.FastScheduler import FastScheduler
from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.infra.scheduler.SchedulerEvent import SchedulerEvent
from protocol0.shared.Logger import Logger


def _default(_, obj):
    # type: (Any, Any) -> Any
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default  # type: ignore[assignment]


class Protocol0(ControlSurface):
    SELF = None  # type: Protocol0

    def __init__(self, c_instance=None):
        # type: (Any, bool) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)
        # noinspection PyProtectedMember
        Protocol0.SELF = self

        self.started = False
        self.song().stop_playing()  # doing this early because the set often loads playing
        # stop log duplication
        self._c_instance.log_message = MethodType(lambda s, message: None, self._c_instance)  # noqa
        self.midi_server_check_timeout_scheduler_event = None  # type: Optional[SchedulerEvent]

        with self.component_guard():
            # setting up scheduler and midi communication system
            MidiManager.set_command_bus(CommandBus)
            SongFacade._song = Song.get_instance()
            self.errorManager = ErrorManager()
            self.songDataManager = SongDataManager()
            self.trackDataManager = TrackDataManager()
            System.get_instance().end_measurement()
            self.deviceManager = DeviceManager()  # needs to be here first
            self.instrumentDisplayManager = InstrumentDisplayManager(self.deviceManager)
            self.instrumentPresetScrollerManager = InstrumentPresetScrollerManager()
            self.trackManager = TrackFactory()
            self.songManager = SongManager()
            self.songTracksManager = SongTracksManager(self.trackManager)
            self.songScenesManager = SongScenesManager()
            self.sessionManager = SessionManager()
            self.mixingManager = MixingManager()
            self.trackRecorderManager = TrackRecorderManager()
            self.clickManager = ClickManager()
            self.automationTrackManager = AutomationTrackManager(self.clickManager)
            self.setFixerManager = SetFixerManager()
            self.setUpgradeManager = SetUpgradeManager()
            self.songStatsManager = SongStatsManager()
            self.audioLatencyAnalyzer = AudioLatencyAnalyzer()
            self.clipManager = ClipManager()
            self.browserManager = BrowserManager()
            self.presetManager = PresetManager()
            self.logManager = LogManager()
            self.validatorManager = ValidatorManager()
            self.sessionToArrangementManager = SessionToArrangementManager()

            # action groups
            ActionGroupFactory.create_action_groups()

            # vocal command
            self.keywordSearchManager = KeywordSearchManager()
            self.vocalCommandManager = VocalCommandManager()

            self.start()

    def start(self):
        # type: () -> None
        self._check_midi_server_is_running()

        self.wait(10, self._check_protocol_midi_is_up)  # waiting for Protocol0_midi to boot

        self.songManager.init_song()

        Logger.log_info("Protocol0 script loaded")
        self.started = True

    def _check_midi_server_is_running(self):
        # type: () -> None
        self.midi_server_check_timeout_scheduler_event = self.wait(300, self._no_midi_server_found)
        System.get_instance().ping()

    def _check_protocol_midi_is_up(self):
        # type: () -> None
        from protocol0_midi import Protocol0Midi
        protocol0_midi = find_if(lambda cs: isinstance(cs, Protocol0Midi), get_control_surfaces())
        if protocol0_midi is None:
            Logger.log_error("Protocol0Midi is not loaded")

    def _no_midi_server_found(self):
        # type: () -> None
        Logger.log_warning("Midi server is not running.")

    def show_message(self, message):
        # type: (str) -> None
        # noinspection PyBroadException
        try:
            super(Protocol0, self).show_message(str(message))
        except Exception:
            Logger.log_warning("Couldn't show message : %s" % message)

    def defer(self, callback):
        # type: (Callable) -> None
        Scheduler.defer(callback)

    def wait(self, tick_count, callback):
        # type: (Union[int, List[int]], Callable) -> Optional[SchedulerEvent]
        """ tick_count (relative to fastScheduler) """
        return Scheduler.wait(tick_count, callback)

    def clear_tasks(self):
        # type: () -> None
        del self._remaining_scheduled_messages[:]
        for seq in reversed(Sequence.RUNNING_SEQUENCES):
            seq.cancel()
        Sequence.RUNNING_SEQUENCES = []
        self._task_group.clear()
        FastScheduler.get_instance().restart()
        Scheduler.clear()

    def disconnect(self):
        # type: () -> None
        ParseUtils._midi_message_registry = {}  # noqa
        super(Protocol0, self).disconnect()
        self.errorManager.disconnect()
        FastScheduler.get_instance().stop()
