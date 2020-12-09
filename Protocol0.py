import inspect
import logging
import types
from typing import Callable

from ClyphX_Pro.clyphx_pro.actions.BrowserActions import BrowserActions

from _Framework.ControlSurface import ControlSurface
from a_protocol_0.components.DeviceManager import DeviceManager
from a_protocol_0.components.Push2Manager import Push2Manager

logger = logging.getLogger(__name__)

from a_protocol_0.components.ActionManager import ActionManager
from a_protocol_0.components.AhkManager import AhkManager
from a_protocol_0.components.ArmManager import ArmManager
from a_protocol_0.components.MidiManager import MidiManager
from a_protocol_0.components.SessionManager import SessionManager
from a_protocol_0.components.SongManager import SongManager
from a_protocol_0.consts import REMOTE_SCRIPTS_FOLDER, LogLevel, ACTIVE_LOG_LEVEL
from a_protocol_0.lom.Song import Song


class Protocol0(ControlSurface):
    def __init__(self, c_instance=None):
        super(Protocol0, self).__init__(c_instance=c_instance)
        # noinspection PyProtectedMember
        self._c_instance.log_message = types.MethodType(lambda s, message: None, self._c_instance)
        with self.component_guard():
            self.protocol0_song = Song(song=self.song())
            self.deviceManager = DeviceManager()
            self.songManager = SongManager()
            self.push2Manager = Push2Manager()
            ArmManager()
            ActionManager()
            self.sessionManager = SessionManager()
            self.ahkManager = AhkManager()
            self.midiManager = MidiManager()
            self.browserManager = BrowserActions()
        self._wait(9, self.protocol0_song.stop)
        self.log_info("Protocol0 script loaded")

    def log_debug(self, message):
        # type: (str) -> None
        self._log(message, LogLevel.DEBUG)

    def log_info(self, message):
        # type: (str) -> None
        self._log(message, LogLevel.INFO, debug=False)

    def _log(self, message, level=LogLevel.INFO, debug=True):
        # type: (str) -> None
        if level < ACTIVE_LOG_LEVEL:
            return
        if debug:
            try:
                cur_frame = inspect.currentframe()
                call_frame = inspect.getouterframes(cur_frame, 2)
                (_, filename, line, method, _, _) = call_frame[1]
                message = "%s (%s:%s in %s)" % (message, filename.replace(REMOTE_SCRIPTS_FOLDER + "\\", ""), line, method)
            except Exception:
                pass
        logger.info(message)

    def defer(self, callback):
        # type: (Callable) -> None
        self._wait(1, callback)

    def wait_bars(self, bar_count, message):
        # type: (int, Callable) -> None
        ticks = round((600 / self.protocol0_song.tempo) * (4 * int(bar_count) - 0.5))
        self._wait(ticks, message)

    def _wait(self, ticks_count, callback):
        # type: (int, Callable) -> None
        self.schedule_message(ticks_count, callback)

    # noinspection PyProtectedMember
    def clear_tasks(self):
        del self._remaining_scheduled_messages[:]
        self._task_group.clear()
