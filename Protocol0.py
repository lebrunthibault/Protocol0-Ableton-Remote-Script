import json
import os
import threading
import traceback
import types

from typing import Callable

from ClyphX_Pro import ClyphXComponentBase
from ClyphX_Pro.SyncedScheduler import SyncedScheduler
from ClyphX_Pro.clyphx_pro.actions.GlobalActions import GlobalActions
from ClyphX_Pro.clyphx_pro.actions.NavAndViewActions import NavAndViewActions
from _Framework.ControlSurface import ControlSurface
from a_protocol_0.components.AutomationTrackManager import AutomationTrackManager
from a_protocol_0.components.BrowserManager import BrowserManager
from a_protocol_0.components.DeviceManager import DeviceManager
from a_protocol_0.components.FastScheduler import FastScheduler
from a_protocol_0.components.KeyBoardShortcutManager import KeyBoardShortcutManager
from a_protocol_0.components.LogManager import LogManager
from a_protocol_0.components.MidiManager import MidiManager
from a_protocol_0.components.MixingManager import MixingManager
from a_protocol_0.components.PlayTrackManager import PlayTrackManager
from a_protocol_0.components.Push2Manager import Push2Manager
from a_protocol_0.components.SessionManager import SessionManager
from a_protocol_0.components.SongManager import SongManager
from a_protocol_0.components.SongStateManager import SongStateManager
from a_protocol_0.components.TrackManager import TrackManager
from a_protocol_0.components.UtilsManager import UtilsManager
from a_protocol_0.components.actionManagers.ActionManager import ActionManager
from a_protocol_0.components.actionManagers.ActionSetManager import ActionSetManager
from a_protocol_0.components.actionManagers.ActionTestManager import ActionTestManager
from a_protocol_0.consts import ROOT_DIR
from a_protocol_0.enums.LogLevelEnum import LogLevelEnum, ACTIVE_LOG_LEVEL
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Song import Song
from a_protocol_0.utils.log import log_ableton


class Protocol0(ControlSurface):
    SELF = None  # type: Protocol0
    LIVE_ENVIRONMENT_LOADED = True

    def __init__(self, c_instance=None, init_song=True):
        super(Protocol0, self).__init__(c_instance=c_instance)
        # noinspection PyProtectedMember
        Protocol0.SELF = self
        self.song().stop_playing()  # doing this early because the set often loads playing
        self._c_instance.log_message = types.MethodType(lambda s, message: None,
                                                        self._c_instance)  # stop log duplication

        self.load_dotenv()  # loading env file

        self._is_dev_booted = False
        self.current_action = None  # type: callable
        with self.component_guard():
            self.protocol0_song = Song(song=self.song())
            self.deviceManager = DeviceManager()  # needs to be here first
            self.songManager = SongManager()
            self.songStateManager = SongStateManager()
            self.sessionManager = SessionManager()
            self.mixingManager = MixingManager()
            self.playTrackManager = PlayTrackManager()
            self.push2Manager = Push2Manager()
            self.trackManager = TrackManager()
            self.automationTrackManager = AutomationTrackManager()
            self.keyboardShortcutManager = KeyBoardShortcutManager()
            self.midiManager = MidiManager()
            self.browserManager = BrowserManager()
            self.clyphxNavigationManager = NavAndViewActions()
            self.clyphxGlobalManager = GlobalActions()
            self.beatScheduler = SyncedScheduler(unschedule_on_stop=True)
            self.fastScheduler = FastScheduler()
            ClyphXComponentBase.start_scheduler()
            self.utilsManager = UtilsManager()
            self.logManager = LogManager()
            self.actionManager = ActionManager()
            self.actionSetManager = ActionSetManager()
            self.actionTestManager = ActionTestManager()
            if init_song:
                self.songManager.init_song()
                self.dev_boot()
        self.log_info("Protocol0 script loaded")

    def post_init(self):
        self.protocol0_song.reset()
        if ACTIVE_LOG_LEVEL == LogLevelEnum.DEBUG:
            self.defer(self.dev_boot)

    def show_message(self, message, log=True):
        # type: (str, bool) -> None
        super(Protocol0, self).show_message(message)
        self.log_warning(message)

    def log_dev(self, message="", debug=True):
        # type: (str) -> None
        self._log(level=LogLevelEnum.DEV, message=message, debug=debug)

    def log_debug(self, *a, **k):
        self._log(level=LogLevelEnum.DEBUG, *a, **k)

    def log_info(self, *a, **k):
        self._log(level=LogLevelEnum.INFO, *a, **k)

    def log_notice(self, *a, **k):
        self._log(level=LogLevelEnum.NOTICE, *a, **k)

    def log_warning(self, *a, **k):
        self._log(level=LogLevelEnum.WARNING, *a, **k)

    def log_error(self, message, debug=True):
        # type: (str) -> None
        self._log(message="%s\n%s" % (message, traceback.format_exc()), level=LogLevelEnum.ERROR, debug=True)
        self.show_message(str(message), log=False)

        if Protocol0.SELF.protocol0_song:
            Protocol0.SELF.protocol0_song.handle_error()

    def _log(self, message="", level=LogLevelEnum.INFO, debug=False):
        # type: (str) -> None
        if level.value < ACTIVE_LOG_LEVEL.value and not debug:
            return
        log_ableton(debug=bool(message) and debug, message=message, level=level, direct_call=False)

    def defer(self, callback):
        # type: (Callable) -> None
        self.fastScheduler.schedule_next(callback)

    def wait_beats(self, beats, callback):
        # type: (int, Callable) -> None
        """ Wait beats uses the clyphx beat scheduler """
        self.beatScheduler.schedule_message("%d" % beats, callback)

    def wait_bars(self, bar_count, callback, exact=False):
        # type: (int, Callable, bool) -> None
        """
            if exact if False, wait_bars executes the callback on the last beat preceding the next <bar_count> bar
            that is if the we are on the 3rd beat in 4/4, the callback will be executed in one beat
            This mode will work when global quantization is set to 1/4 or more
        """
        beat_offset = 0 if exact else self.protocol0_song.get_current_beats_song_time().beats
        beat_count = (self.protocol0_song.signature_denominator * bar_count) - beat_offset
        self.wait_beats(beat_count, callback)

    def _wait(self, duration, callback):
        # type: (int, callable) -> None
        """ duration in ms (execution is not ms precise) """
        assert duration >= 0
        assert callable(callback)
        if duration == 0:
            callback()
        else:
            # for ticks_count > 1 we use the 100ms timer losing some speed but it's easier for now
            if Protocol0.LIVE_ENVIRONMENT_LOADED:
                self.fastScheduler.schedule(timeout_duration=duration, callback=callback)
            else:
                # emulate schedule_message
                threading.Timer(float(duration) / 1000, callback).start()

    def clear_tasks(self):
        del self._remaining_scheduled_messages[:]
        self._task_group.clear()

    def dev_boot(self):
        if self._is_dev_booted:
            return

    def load_dotenv(self):
        """ doing this manually because dotenv throws an encoding error """
        with open("%s/.env.json" % ROOT_DIR) as f:
            env_vars = json.loads(f.read())
            for key, value in env_vars.iteritems():
                os.environ[key] = value

    def disconnect(self):
        pass
        # self._scheduler.stop()
