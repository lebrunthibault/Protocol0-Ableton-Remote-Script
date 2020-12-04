import inspect
import logging
import types
from typing import Callable, Any

from _Framework.ControlSurface import ControlSurface
from a_protocol_0.devices.InstrumentManager import InstrumentManager

logger = logging.getLogger(__name__)

from a_Push2.push2 import Push2
from a_protocol_0.components.ActionManager import ActionManager
from a_protocol_0.components.AhkManager import AhkManager
from a_protocol_0.components.ArmManager import ArmManager
from a_protocol_0.components.MidiManager import MidiManager
from a_protocol_0.components.SessionManager import SessionManager
from a_protocol_0.components.SongManager import SongManager
from a_protocol_0.consts import REMOTE_SCRIPTS_FOLDER
from a_protocol_0.lom.Song import Song
from a_protocol_0.utils.config import Config


class Protocol0(ControlSurface):
    SELF = None  # type: Protocol0

    def __init__(self, c_instance=None):
        super(Protocol0, self).__init__(c_instance=c_instance)
        Protocol0.SELF = self
        # noinspection PyProtectedMember
        self._c_instance.log_message = types.MethodType(lambda s, message: None, self._c_instance)
        with self.component_guard():
            self.protocol0_song = Song(song=self.song())
            self.instrumentManager = InstrumentManager()
            ArmManager()
            ActionManager()
            self.songManager = SongManager()
            self.sessionManager = SessionManager()
            self.ahkManager = AhkManager()
            self.midiManager = MidiManager()

        self._wait(9, self.protocol0_song.stop)
        Push2.protocol0 = self
        self.log("Protocol0 script loaded")

    def log(self, message, debug=True):
        # type: (str) -> None
        try:
            cur_frame = inspect.currentframe()
            call_frame = inspect.getouterframes(cur_frame, 2)
            (_, filename, line, method, _, _) = call_frame[1]
        except Exception:
            filename = None
        if Config.DEBUG and debug and filename:
            message = "%s (%s:%s in %s)" % (message, filename.replace(REMOTE_SCRIPTS_FOLDER + "\\", ""), line, method)
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
