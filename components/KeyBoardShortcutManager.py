import subprocess
from os.path import expanduser

from typing import Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import PROTOCOL0_FOLDER
from a_protocol_0.utils.decorators import log

home = expanduser("~")


class KeyBoardShortcutManager(AbstractControlSurfaceComponent):
    def __init__(self):
        # launch the main ahk script
        subprocess.Popen(["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
                          PROTOCOL0_FOLDER + "\\scripts\\ahk\\ableton_shortcuts.ahk"])

    def _execute_python(self, filename, *args):
        # type: (str, Any) -> int
        parameters = ["pythonw.exe", PROTOCOL0_FOLDER + "\\scripts\\python\\%s" % filename]
        for arg in args:
            parameters.append(str(arg))

        child = subprocess.Popen(parameters)
        child.communicate()
        return child.returncode

    def _execute_ahk(self, filename, *args):
        # type: (str, Any) -> int
        parameters = ["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
                      PROTOCOL0_FOLDER + "\\scripts\\ahk\\%s" % filename]
        for arg in args:
            parameters.append(str(arg))

        child = subprocess.Popen(parameters)
        child.communicate()
        return child.returncode

    @log
    def send_keys(self, keys):
        # type: (str) -> None
        self._execute_python("send_keys.py", keys)

    @log
    def send_click(self, x, y):
        # type: (int, int) -> None
        self._execute_python("send_click.py", x, y)

    def show_hide_plugins(self):
        self.send_keys("^%p")

    def show_plugins(self):
        self.send_keys("^{F1}")

    def hide_plugins(self):
        self.send_keys("^{F2}")

    def toggle_device_button(self, x, y, activate=True):
        # type: (int, int) -> None
        self._execute_ahk("deactivate_ableton_button.ahk", str(x), str(y), "1" if activate else "0")

    def is_plugin_window_visible(self, plugin_name=""):
        # type: (str) -> bool
        """ we cannot do this inside of ahk because the sleeping prevents the window to show """
        return bool(self._execute_ahk("show_plugins_and_check.ahk", str(plugin_name)))

    def show_and_activate_rev2_editor(self):
        self.send_keys("^{F3}")

    def group_track(self):
        self.send_keys("^{F4}")

    def up(self):
        self.send_keys("^{F5}")

    def duplicate(self):
        self.send_keys("^d")
