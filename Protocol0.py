import threading
from json import JSONEncoder
from types import MethodType

from ClyphX_Pro import ParseUtils
from p0_system_api import P0SystemAPI
from typing import Callable, Any, Optional

# noinspection PyUnresolvedReferences
from _Framework.ControlSurface import ControlSurface, get_control_surfaces
from protocol0.components.AutomationTrackManager import AutomationTrackManager
from protocol0.components.BrowserManager import BrowserManager
from protocol0.components.ClipManager import ClipManager
from protocol0.components.DeviceManager import DeviceManager
from protocol0.components.ErrorManager import ErrorManager
from protocol0.components.LogManager import LogManager
from protocol0.components.MidiManager import MidiManager
from protocol0.components.MixingManager import MixingManager
from protocol0.components.NavigationManager import NavigationManager
from protocol0.components.PresetManager import PresetManager
from protocol0.components.QuantizationManager import QuantizationManager
from protocol0.components.SessionManager import SessionManager
from protocol0.components.SessionToArrangementManager import SessionToArrangementManager
from protocol0.components.SongDataManager import SongDataManager
from protocol0.components.SongManager import SongManager
from protocol0.components.TrackDataManager import TrackDataManager
from protocol0.components.TrackManager import TrackManager
from protocol0.components.UtilsManager import UtilsManager
from protocol0.components.ValidatorManager import ValidatorManager
from protocol0.components.action_groups.ActionGroupData import ActionGroupData
from protocol0.components.action_groups.ActionGroupFix import ActionGroupFix
from protocol0.components.action_groups.ActionGroupLog import ActionGroupLog
from protocol0.components.action_groups.ActionGroupMain import ActionGroupMain
from protocol0.components.action_groups.ActionGroupMix import ActionGroupMix
from protocol0.components.action_groups.ActionGroupPreset import ActionGroupPreset
from protocol0.components.action_groups.ActionGroupSet import ActionGroupSet
from protocol0.components.action_groups.ActionGroupTest import ActionGroupTest
from protocol0.components.api.ApiAction import ApiAction
from protocol0.components.api.ApiRoutesManager import ApiRoutesManager
from protocol0.components.audit.AudioLatencyAnalyzer import AudioLatencyAnalyzer
from protocol0.components.audit.SetFixerManager import SetFixerManager
from protocol0.components.audit.SetUpgradeManager import SetUpgradeManager
from protocol0.components.audit.SongStatsManager import SongStatsManager
from protocol0.components.lom.SongScenesManager import SongScenesManager
from protocol0.components.lom.SongTracksManager import SongTracksManager
from protocol0.components.scheduler.BeatScheduler import BeatScheduler
from protocol0.components.scheduler.FastScheduler import FastScheduler, SchedulerEvent
from protocol0.components.vocal_command.KeywordSearchManager import KeywordSearchManager
from protocol0.components.vocal_command.VocalCommandManager import VocalCommandManager
from protocol0.config import Config
from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.lom.Application import Application
from protocol0.lom.Song import Song
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.log import log_ableton
from protocol0.utils.utils import find_if


def _default(_, obj):
    # type: (Any, Any) -> Any
    return getattr(obj.__class__, "to_json_dict", _default.default)(obj)


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
        self.protocol0_song = None  # type: Optional[Song]
        self.midi_server_check_timeout_scheduler_event = None  # type: Optional[SchedulerEvent]

        with self.component_guard():
            # setting up scheduler and midi communication system
            self.errorManager = ErrorManager()
            self.fastScheduler = FastScheduler()
            self.midiManager = MidiManager()
            ApiRoutesManager()
            ApiAction.create_method_mapping()
            self.p0_system_api_client = P0SystemAPI()
            self.protocol0_application = Application()
            self.protocol0_song = Song(song=self.song())
            self.songDataManager = SongDataManager()
            self.trackDataManager = TrackDataManager()
            if Config.SHOW_RELOAD_TIME or Config.ABLETON_SESSION_TYPE == AbletonSessionTypeEnum.PROFILING:
                self.p0_system_api_client.end_measurement()

            self.deviceManager = DeviceManager()  # needs to be here first
            AbstractInstrument.INSTRUMENT_CLASSES = AbstractInstrument.get_instrument_classes()
            self.songManager = SongManager()
            self.songTracksManager = SongTracksManager()
            self.songScenesManager = SongScenesManager()
            self.sessionManager = SessionManager()
            self.mixingManager = MixingManager()
            self.trackManager = TrackManager()
            self.automationTrackManager = AutomationTrackManager()
            self.quantizationManager = QuantizationManager()
            self.setFixerManager = SetFixerManager()
            self.setUpgradeManager = SetUpgradeManager()
            self.songStatsManager = SongStatsManager()
            self.audioLatencyAnalyzer = AudioLatencyAnalyzer()
            self.clipManager = ClipManager()
            self.browserManager = BrowserManager()
            self.navigationManager = NavigationManager()
            self.presetManager = PresetManager()
            self._beatScheduler = BeatScheduler()
            self.utilsManager = UtilsManager()
            self.logManager = LogManager()
            self.validatorManager = ValidatorManager()
            self.sessionToArrangementManager = SessionToArrangementManager()
            # return

            if Config.ABLETON_SESSION_TYPE != AbletonSessionTypeEnum.TEST:
                # action groups
                ActionGroupData()
                ActionGroupFix()
                ActionGroupLog()
                ActionGroupMain()
                ActionGroupMix()
                ActionGroupPreset()
                ActionGroupSet()
                ActionGroupTest()

                # vocal command
                self.keywordSearchManager = KeywordSearchManager()
                self.vocalCommandManager = VocalCommandManager()

                self.start()

    @property
    def system(self):
        # type: () -> P0SystemAPI
        """
        Access to non restricted (system) python environment over MIDI
        """
        return self.p0_system_api_client

    def start(self):
        # type: () -> None
        if Config.ABLETON_SESSION_TYPE == AbletonSessionTypeEnum.NORMAL:
            self._check_midi_server_is_running()

        self.wait(10, self._check_protocol_midi_is_up)  # waiting for Protocol0_midi to boot

        # self.wait(100, self.push2Manager.connect_push2)
        # self.wait(200, self.push2Manager.connect_push2)
        # self.wait(400, partial(self.push2Manager.connect_push2, log=True))

        self.navigationManager.show_session()

        self.songManager.init_song()

        self.log_info("Protocol0 script loaded")
        self.started = True

    def _check_midi_server_is_running(self):
        # type: () -> None
        self.midi_server_check_timeout_scheduler_event = self.wait(300, self._no_midi_server_found)
        self.system.ping()

    def _check_protocol_midi_is_up(self):
        # type: () -> None
        from protocol0_midi import Protocol0Midi
        protocol0_midi = find_if(lambda cs: isinstance(cs, Protocol0Midi), get_control_surfaces())
        if protocol0_midi is None:
            self.log_error("Protocol0Midi is not loaded")

    def _no_midi_server_found(self):
        # type: () -> None
        self.log_warning("Midi server is not running.")

    def show_message(self, message, log=True):
        # type: (str, bool) -> None
        # noinspection PyBroadException
        try:
            super(Protocol0, self).show_message(message)
        except Exception:
            self.log_warning("Couldn't show message")
        if log:
            self.log_warning(message)

    def log_dev(self, message="", debug=True):
        # type: (Any, bool) -> None
        self._log(level=LogLevelEnum.DEV, message=message, debug=debug)

    def log_debug(self, *a, **k):
        # type: (Any, Any) -> None
        self._log(level=LogLevelEnum.DEBUG, *a, **k)

    def log_info(self, *a, **k):
        # type: (Any, Any) -> None
        self._log(level=LogLevelEnum.INFO, *a, **k)

    def log_notice(self, *a, **k):
        # type: (Any, Any) -> None
        self._log(level=LogLevelEnum.NOTICE, *a, **k)

    def log_warning(self, *a, **k):
        # type: (Any, Any) -> None
        self._log(level=LogLevelEnum.WARNING, *a, **k)

    def log_error(self, message="", debug=True, show_message=True):
        # type: (str, bool, bool) -> None
        self._log(message, level=LogLevelEnum.ERROR, debug=debug)
        if show_message:
            # noinspection PyBroadException
            try:
                super(Protocol0, self).show_message(message)
            except Exception:
                self.log_warning("Couldn't show message")

    def _log(self, message="", level=LogLevelEnum.INFO, debug=False):
        # type: (Any, LogLevelEnum, bool) -> None
        if not isinstance(message, basestring):
            message = str(message)
        log_ableton(
            message=message,
            debug=message is not None and debug,
            level=level,
            direct_call=False,
        )

    def defer(self, callback):
        # type: (Callable) -> None
        self.fastScheduler.schedule_next(callback)

    def defer_low(self, callback):
        # type: (Callable) -> None
        self.schedule_message(1, callback)

    def wait_bars(self, bar_length, callback):
        # type: (int, Callable) -> None
        self._beatScheduler.wait_bars(bar_length, callback)

    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        self._beatScheduler.wait_beats(beats, callback)

    def wait(self, tick_count, callback):
        # type: (int, Callable) -> Optional[SchedulerEvent]
        """ tick_count (relative to fastScheduler) """
        assert callable(callback)
        if tick_count == 0:
            callback()
            return None
        else:
            if not Config.ABLETON_SESSION_TYPE == AbletonSessionTypeEnum.TEST:
                return self.fastScheduler.schedule(tick_count=tick_count, callback=callback)
            else:
                # callback()  # no scheduling when testing
                # emulate scheduler
                threading.Timer(
                    float(tick_count) * self.fastScheduler.TICK_MS_DURATION / 1000,
                    callback,
                ).start()
                return None

    def clear_tasks(self):
        # type: () -> None
        del self._remaining_scheduled_messages[:]
        for seq in reversed(Sequence.RUNNING_SEQUENCES):
            seq.cancel()
        Sequence.RUNNING_SEQUENCES = []
        self._task_group.clear()
        self.fastScheduler.restart()
        self._beatScheduler.clear_scheduler()

    def disconnect(self):
        # type: () -> None
        ParseUtils._midi_message_registry = {}  # noqa
        super(Protocol0, self).disconnect()
        self.errorManager.disconnect()
        self.fastScheduler.stop()
