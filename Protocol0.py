import threading
from types import MethodType

from ClyphX_Pro import ClyphXComponentBase, ParseUtils
from ClyphX_Pro.clyphx_pro.actions.GlobalActions import GlobalActions
from a_protocol_0.automation.AutomationTrackManager import AutomationTrackManager
from a_protocol_0.components.Api.ApiManager import ApiManager
from a_protocol_0.components.BeatScheduler import BeatScheduler
from a_protocol_0.components.BrowserManager import BrowserManager
from a_protocol_0.components.DeviceManager import DeviceManager
from a_protocol_0.components.ErrorManager import ErrorManager
from a_protocol_0.components.FastScheduler import FastScheduler
from a_protocol_0.components.LogManager import LogManager
from a_protocol_0.components.MidiManager import MidiManager
from a_protocol_0.components.MixingManager import MixingManager
from a_protocol_0.components.NavigationManager import NavigationManager
from a_protocol_0.components.Push2Manager import Push2Manager
from a_protocol_0.components.QuantizationManager import QuantizationManager
from a_protocol_0.components.SearchManager import SearchManager
from a_protocol_0.components.SessionManager import SessionManager
from a_protocol_0.components.SetFixerManager import SetFixerManager
from a_protocol_0.components.SongManager import SongManager
from a_protocol_0.components.TrackManager import TrackManager
from a_protocol_0.components.UtilsManager import UtilsManager
from a_protocol_0.components.actionGroups.ActionGroupMain import ActionGroupMain
from a_protocol_0.components.actionGroups.ActionGroupSet import ActionGroupSet
from a_protocol_0.components.actionGroups.ActionGroupTest import ActionGroupTest
from a_protocol_0.config import Config
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.LogLevelEnum import LogLevelEnum
from a_protocol_0.lom.Song import Song
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.log import log_ableton
from p0_system_api import DefaultApi
from typing import Callable, Any

from _Framework.ControlSurface import ControlSurface


class Protocol0(ControlSurface):
    SELF = None  # type: Protocol0
    LIVE_ENVIRONMENT_LOADED = True

    def __init__(self, c_instance=None, test_mode=False):
        # type: (Any, bool) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)
        # noinspection PyProtectedMember
        Protocol0.SELF = self
        self.test_mode = test_mode
        self.started = False
        self.song().stop_playing()  # doing this early because the set often loads playing
        # stop log duplication
        self._c_instance.log_message = MethodType(lambda s, message: None, self._c_instance)  # noqa

        AbstractInstrument.INSTRUMENT_CLASSES = AbstractInstrument.get_instrument_classes()

        with self.component_guard():
            self.errorManager = ErrorManager(set_excepthook=False)
            self.protocol0_song = Song(song=self.song())
            self.fastScheduler = FastScheduler()
            self.deviceManager = DeviceManager()  # needs to be here first
            self.songManager = SongManager()
            self.sessionManager = SessionManager()
            MixingManager()
            self.push2Manager = Push2Manager()
            self.trackManager = TrackManager()
            self.automationTrackManager = AutomationTrackManager()
            self.quantizationManager = QuantizationManager()
            self.setFixerManager = SetFixerManager()
            self.midiManager = MidiManager()
            self.browserManager = BrowserManager()
            self.navigationManager = NavigationManager()
            GlobalActions()
            self.globalBeatScheduler = BeatScheduler()
            self.sceneBeatScheduler = BeatScheduler()
            self.utilsManager = UtilsManager()
            self.logManager = LogManager()
            self.searchManager = SearchManager()
            self.apiManager = ApiManager()
            self.p0_system_api_client = DefaultApi()
            ActionGroupMain()
            ActionGroupSet()
            ActionGroupTest()

            self.start()

            self.log_info("Protocol0 script loaded")

    def start(self):
        # type: () -> None
        ClyphXComponentBase.start_scheduler()
        self.fastScheduler.restart()
        if not self.test_mode:
            self.defer(self.songManager.init_song)
        self.started = True

    def show_message(self, message, log=True):
        # type: (str, bool) -> None
        super(Protocol0, self).show_message(message)
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

    def log_error(self, message="", debug=True):
        # type: (str, bool) -> None
        self._log(message, level=LogLevelEnum.ERROR, debug=debug)

    def _log(self, message="", level=LogLevelEnum.INFO, debug=False):
        # type: (Any, LogLevelEnum, bool) -> None
        if not isinstance(message, basestring):
            message = str(message)
        if level.value < Config.LOG_LEVEL.value:
            return
        log_ableton(
            message=message,
            debug=message is not None and debug,
            level=level,
            direct_call=False,
        )

    def defer(self, callback):
        # type: (Callable) -> None
        self.fastScheduler.schedule_next(callback)

    def wait_bars(self, bar_length, callback):
        # type: (int, Callable) -> None
        self.globalBeatScheduler.wait_bars(bar_length, callback)

    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        self.globalBeatScheduler.wait_beats(beats, callback)

    def _wait(self, tick_count, callback):
        # type: (int, Callable) -> None
        """ tick_count (relative to fastScheduler) """
        assert callable(callback)
        if tick_count == 0:
            callback()
        else:
            # for ticks_count > 1 we use the 100ms timer losing some speed but it's easier for now
            if Protocol0.LIVE_ENVIRONMENT_LOADED:
                self.fastScheduler.schedule(tick_count=tick_count, callback=callback)
            else:
                # emulate schedule_message
                threading.Timer(
                    float(tick_count) * self.fastScheduler.TICK_MS_DURATION / 1000,
                    callback,
                ).start()

    def clear_tasks(self):
        # type: () -> None
        del self._remaining_scheduled_messages[:]
        for seq in Sequence.RUNNING_SEQUENCES:
            seq.terminate()
        self._task_group.clear()
        self.fastScheduler.restart()
        self.globalBeatScheduler.clear()

    def disconnect(self):
        # type: () -> None
        ParseUtils._midi_message_registry = {}  # noqa
        super(Protocol0, self).disconnect()
        self.fastScheduler.stop()
