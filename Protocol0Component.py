import inspect
import types
from typing import Callable, Any

from _Framework.CompoundComponent import CompoundComponent
from _Framework.Dependency import inject, depends
from _Framework.Util import const

from Push2.push2 import Push2
from a_protocol_0 import Protocol0
from a_protocol_0.components.ActionManager import ActionManager
from a_protocol_0.components.AhkCommands import AhkCommands
from a_protocol_0.components.ArmManager import ArmManager
from a_protocol_0.components.MidiActions import MidiActions
from a_protocol_0.components.SessionManager import SessionManager
from a_protocol_0.consts import REMOTE_SCRIPTS_FOLDER
from a_protocol_0.lom.Song import Song
from a_protocol_0.utils.config import Config


class Protocol0Component(CompoundComponent):
    SELF = None

    @depends(send_midi=None)
    def __init__(self, control_surface, send_midi=None, *a, **k):
        # type: (Protocol0, callable, Any, Any) -> None
        super(Protocol0Component, self).__init__(*a, **k)
        Protocol0Component.SELF = self
        Push2.protocol0 = self
        self.control_surface = control_surface
        # noinspection PyProtectedMember
        self.canonical_parent._c_instance.log_message = types.MethodType(lambda s, message: None, self.canonical_parent._c_instance)
        self.song = Song()
        with inject(send_midi=const(send_midi), parent=const(self), my_song=const(self.song)).everywhere():
            ArmManager()
            ActionManager()
            self.sessionManager = SessionManager()
            self.ahk_commands = AhkCommands()
            self.midi = MidiActions()
        self.log("Protocol0 script loaded")

    def log(self, message):
        # type: (str) -> None
        cur_frame = inspect.currentframe()
        call_frame = inspect.getouterframes(cur_frame, 2)
        (_, filename, line, method, _, _) = call_frame[1]
        if Config.DEBUG:
            message = "%s (%s:%s in %s)" % (message, filename.replace(REMOTE_SCRIPTS_FOLDER + "\\", ""), line, method)
        self.canonical_parent.log_message(message)

    def show_message(self, message):
        # type: (str) -> None
        self.canonical_parent.show_message(message)

    def defer(self, callback):
        # type: (Callable) -> None
        self._wait(1, callback)

    def wait_bars(self, bar_count, message):
        # type: (int, Callable) -> None
        self._wait(self.song.bar_count_length(bar_count), message)

    def _wait(self, ticks_count, callback):
        # type: (int, Callable) -> None
        self.canonical_parent.schedule_message(ticks_count, callback)

    # noinspection PyProtectedMember
    def clear_tasks(self):
        del self.canonical_parent._remaining_scheduled_messages[:]
        self.canonical_parent._task_group.clear()

    def disconnect(self):
        super(Protocol0Component, self).disconnect()
