import subprocess
from functools import partial
from os.path import expanduser

from typing import Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import PROTOCOL0_FOLDER
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import log

home = expanduser("~")


class KeyBoardShortcutManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(KeyBoardShortcutManager, self).__init__(*a, **k)
        # launch the main ahk script
        subprocess.Popen(["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
                          PROTOCOL0_FOLDER + "\\scripts\\ahk\\ableton_shortcuts.ahk"])

    def _execute_python(self, filename, *args):
        # type: (str, Any) -> int
        python3_exe = "C:\\Users\\thiba\\AppData\\Local\\Programs\\Python\\Python39\\pythonw.exe"
        # parameters = ["pythonw", PROTOCOL0_FOLDER + "\\scripts\\python\\%s" % filename]
        parameters = [python3_exe, PROTOCOL0_FOLDER + "\\scripts\\python\\%s" % filename]
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
    def send_keys(self, keys, repeat=False):
        # type: (str, bool) -> None
        seq = Sequence()
        seq.add(self.parent.clyphxNavigationManager.focus_main)
        seq.add(partial(self._execute_python, "send_keys.py", keys))
        if repeat:
            # here trying to mitigate shortcuts not received by Live god knows why ..
            seq.add(wait=1)
            seq.add(partial(self._execute_python, "send_keys.py", keys))

        return seq.done()

    def focus_window(self, window_name):
        # type: (str) -> None
        seq = Sequence(bypass_errors=True, debug=False)
        seq.add(self.parent.clyphxNavigationManager.focus_main)
        seq.add(partial(self._execute_python, "focus_window.py", window_name))

        return seq.done()

    def focus_logs(self):
        return self.focus_window("logs terminal")

    @log
    def send_click(self, x, y):
        # type: (int, int) -> None
        self._execute_python("send_click.py", x, y)

    def show_hide_plugins(self):
        self.send_keys("^%p")

    def show_plugins(self):
        self.send_keys("^{F1}", repeat=True)

    def hide_plugins(self):
        self.send_keys("^{F2}", repeat=True)

    def toggle_device_button(self, x, y, activate=True):
        # type: (int, int) -> None
        self._execute_python("toggle_ableton_button.py", str(x), str(y), "1" if activate else "0")

    def is_plugin_window_visible(self, plugin_name=""):
        # type: (str) -> bool
        """ we cannot do this inside of ahk because the sleeping prevents the window to show """
        return bool(self._execute_ahk("show_plugins_and_check.ahk", str(plugin_name)))

    def show_and_activate_rev2_editor(self):
        self.send_keys("^{F3}")

    def group_track(self):
        self.send_keys("^{F4}")

    def up(self):
        self.send_keys("^{F5}", repeat=True)

    def duplicate(self):
        self.send_keys("^d")
