import threading
from functools import partial
from json import JSONEncoder
from types import MethodType

from ClyphX_Pro import ParseUtils
from ClyphX_Pro.clyphx_pro.actions.GlobalActions import GlobalActions
from p0_system_api import P0SystemAPI
from typing import Callable, Any, Optional

# noinspection PyUnresolvedReferences
from _Framework.ControlSurface import ControlSurface
from protocol0.components.AutomationTrackManager import AutomationTrackManager
from protocol0.components.BeatScheduler import BeatScheduler
from protocol0.components.BrowserManager import BrowserManager
from protocol0.components.ClipManager import ClipManager
from protocol0.components.DeviceManager import DeviceManager
from protocol0.components.ErrorManager import ErrorManager
from protocol0.components.scheduler.FastScheduler import FastScheduler, SchedulerEvent
from protocol0.components.LogManager import LogManager
from protocol0.components.MidiManager import MidiManager
from protocol0.components.MixingManager import MixingManager
from protocol0.components.NavigationManager import NavigationManager
from protocol0.components.PresetManager import PresetManager
from protocol0.components.Push2Manager import Push2Manager
from protocol0.components.QuantizationManager import QuantizationManager
from protocol0.components.SessionManager import SessionManager
from protocol0.components.SetFixerManager import SetFixerManager
from protocol0.components.SongDataManager import SongDataManager
from protocol0.components.SongManager import SongManager
from protocol0.components.TrackManager import TrackManager
from protocol0.components.UtilsManager import UtilsManager
from protocol0.components.ValidatorManager import ValidatorManager
from protocol0.components.action_groups.ActionGroupMain import ActionGroupMain
from protocol0.components.action_groups.ActionGroupPreset import ActionGroupPreset
from protocol0.components.action_groups.ActionGroupSet import ActionGroupSet
from protocol0.components.action_groups.ActionGroupTest import ActionGroupTest
from protocol0.components.api.ApiAction import ApiAction
from protocol0.components.vocal_command.KeywordSearchManager import KeywordSearchManager
from protocol0.components.vocal_command.VocalCommandManager import VocalCommandManager
from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.Song import Song
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.log import log_ableton


def _default(_, obj):
    # type: (Any, Any) -> Any
    return getattr(obj.__class__, "to_json_dict", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default  # type: ignore[assignment]


class Protocol0(ControlSurface):
    SELF = None  # type: Protocol0

    def __init__(self, c_instance=None, test_mode=False):
        # type: (Any, bool) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)
        # noinspection PyProtectedMember
        Protocol0.SELF = self
        if self._is_ableton_template_set:
            P0SystemAPI().reload_ableton()
            return

        self.test_mode = test_mode
        self.started = False
        self.song().stop_playing()  # doing this early because the set often loads playing
        # stop log duplication
        self._c_instance.log_message = MethodType(lambda s, message: None, self._c_instance)  # noqa

        AbstractInstrument.INSTRUMENT_CLASSES = AbstractInstrument.get_instrument_classes()

        with self.component_guard():
            self.p0_system_api_client = P0SystemAPI()
            self.errorManager = ErrorManager()
            self.protocol0_song = Song(song=self.song())
            self.fastScheduler = FastScheduler()
            self.deviceManager = DeviceManager()  # needs to be here first
            self.songManager = SongManager()
            self.songDataManager = SongDataManager()
            self.sessionManager = SessionManager()
            MixingManager()
            if not test_mode:
                self.push2Manager = Push2Manager()
            self.trackManager = TrackManager()
            self.automationTrackManager = AutomationTrackManager()
            self.quantizationManager = QuantizationManager()
            self.setFixerManager = SetFixerManager()
            self.midiManager = MidiManager()
            self.clipManager = ClipManager()
            self.browserManager = BrowserManager()
            self.navigationManager = NavigationManager()
            self.presetManager = PresetManager()
            GlobalActions()
            self.globalBeatScheduler = BeatScheduler()
            self.sceneBeatScheduler = BeatScheduler()
            self.utilsManager = UtilsManager()
            self.logManager = LogManager()
            self.validatorManager = ValidatorManager()

            if not test_mode:
                # action groups
                ActionGroupMain()
                ActionGroupSet()
                ActionGroupPreset()
                ActionGroupTest()

                # vocal command
                self.keywordSearchManager = KeywordSearchManager()
                VocalCommandManager()

                self.songDataManager.restore_data()

                ApiAction.create_method_mapping()

                self.start()

    def start(self):
        # type: () -> None
        if self.test_mode:
            return

        InterfaceState.SELECTED_RECORDING_BAR_LENGTH = BarLengthEnum.ONE
        InterfaceState.RECORD_CLIP_TAILS = True
        InterfaceState.SELECTED_CLIP_TAILS_BAR_LENGTH = BarLengthEnum.ONE

        self.wait(100, self.push2Manager.connect_push2)
        self.wait(200, self.push2Manager.connect_push2)
        self.wait(400, partial(self.push2Manager.connect_push2, log=True))

        self.navigationManager.show_session()

        if not self.test_mode:
            self.defer(self.songManager.init_song)

        self.log_info("Protocol0 script loaded")
        self.started = True

    @property
    def _is_ableton_template_set(self):
        # type: () -> bool
        return len(list(self.song().tracks)) == 2 and len(self.song().scenes) == 20

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

    def log_error(self, message="", debug=True):
        # type: (str, bool) -> None
        self._log(message, level=LogLevelEnum.ERROR, debug=debug)

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
        self.globalBeatScheduler.wait_bars(bar_length, callback)

    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        self.globalBeatScheduler.wait_beats(beats, callback)

    def wait(self, tick_count, callback):
        # type: (int, Callable) -> Optional[SchedulerEvent]
        """ tick_count (relative to fastScheduler) """
        assert callable(callback)
        if tick_count == 0:
            callback()
            return None
        else:
            # for ticks_count > 1 we use the 100ms timer losing some speed but it's easier for now
            if not self.test_mode:
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
            seq.terminate()
        self._task_group.clear()
        self.fastScheduler.restart()
        self.globalBeatScheduler.clear()

    def disconnect(self):
        # type: () -> None
        ParseUtils._midi_message_registry = {}  # noqa
        super(Protocol0, self).disconnect()
        self.errorManager.disconnect()
        self.fastScheduler.stop()
