import os
import subprocess
from functools import partial

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import CLI_PATH
from a_protocol_0.enums.ColorEnum import InterfaceColorEnum
from a_protocol_0.enums.CommandEnum import CommandEnum
from a_protocol_0.enums.PixelEnum import PixelEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import log
from typing import Any, Optional


class CommandManager(AbstractControlSurfaceComponent):
    def execute(self, command, *args):
        # type: (CommandEnum, Any) -> int
        args = (command.name,) + args
        self.parent.log_dev((CLI_PATH, args))
        return self._execute_program(str(os.getenv("PYTHONW_EXE")), CLI_PATH, *args)

    @classmethod
    def execute_batch(self, filename):
        # type: (str) -> int
        return self._execute_program(None, filename)

    @staticmethod
    def _execute_program(program, filename, *args):
        # type: (Optional[str], str, Any) -> int
        if not os.path.exists(filename):
            raise Protocol0Error("incorrect script path: %s" % filename)

        if program is None:
            subprocess.Popen(filename, shell=True)
            return 0
        else:
            parameters = [program, filename]
            for arg in args:
                parameters.append(str(arg))

            child = subprocess.Popen(parameters)
            child.communicate()
            return child.returncode

    @log
    def send_keys(self, keys, repeat=False):
        # type: (str, bool) -> Sequence
        seq = Sequence(silent=True)
        seq.add(self.parent.navigationManager.focus_main)
        seq.add(partial(self.execute, CommandEnum.SEND_KEYS, keys))
        if repeat:
            # here trying to mitigate shortcuts not received by Live god knows why ..
            seq.add(wait=5)
            seq.add(partial(self.execute, CommandEnum.SEND_KEYS, keys))

        return seq.done()

    def focus_window(self, window_name):
        # type: (str) -> Sequence
        seq = Sequence(bypass_errors=True, silent=True)
        seq.add(self.parent.navigationManager.focus_main)
        seq.add(partial(self.execute, CommandEnum.FOCUS_WINDOW, window_name))

        return seq.done()

    def focus_logs(self):
        # type: () -> None
        self.focus_window("logs terminal")

    def send_click(self, x, y):
        # type: (int, int) -> None
        self.execute(CommandEnum.SEND_CLICK, x, y)

    def show_hide_plugins(self):
        # type: () -> None
        self.send_keys("^%p")

    def show_plugins(self):
        # type: () -> None
        self.send_keys("^{F1}")

    def hide_plugins(self):
        # type: () -> None
        self.send_keys("^{F2}")

    def click_clip_fold_notes(self):
        # type: () -> None
        self.send_click(x=418, y=686)
        self.send_click(x=418, y=686)

    def double_click_envelopes_show_box(self):
        # type: () -> None
        self.send_click(x=86, y=1014)
        self.send_click(x=86, y=1014)

    def toggle_device_button(self, x, y, activate=True):
        # type: (int, int, bool) -> None
        self.execute(CommandEnum.TOGGLE_ABLETON_BUTTON, str(x), str(y), "1" if activate else "0")

    def pixel_has_color(self, pixel, color):
        # type: (PixelEnum, InterfaceColorEnum) -> bool
        (x, y) = pixel.value
        return bool(self.execute(CommandEnum.PIXEL_HAS_COLOR, str(x), str(y), color.value))

    def is_plugin_window_visible(self, plugin_name):
        # type: (str) -> bool
        """ we cannot do ctrl alt p and recheck inside of ahk because the sleeping prevents the window to show """
        return bool(self.execute(CommandEnum.IS_PLUGIN_WINDOW_VISIBLE, str(plugin_name)))

    def show_and_activate_rev2_editor(self):
        # type: () -> None
        """ the activation button can be at 2 positions depending on idk what"""
        self.show_plugins()
        self.execute(CommandEnum.ACTIVATE_REV2_EDITOR)

    def group_track(self):
        # type: () -> None
        self.send_keys("^{F4}")

    def up(self):
        # type: () -> None
        self.send_keys("^{F5}", repeat=True)
