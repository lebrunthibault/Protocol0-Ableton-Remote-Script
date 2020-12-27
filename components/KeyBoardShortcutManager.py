import subprocess
from os.path import expanduser

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.decorators import defer

home = expanduser("~")


class KeyBoardShortcutManager(AbstractControlSurfaceComponent):
    def send_keys(self, keys):
        # type: (str) -> None
        self.parent.log_info("Sending keys : " + keys)
        subprocess.Popen(["pythonw.exe",
                          home + "\\Google Drive\\music\\dev\\scripts\\python\\sendKeys.py",
                          keys]
                         ).communicate()

    def send_click(self, x, y):
        # type: (int, int) -> None
        self.send_keys("%d,%d" % (x, y))

    def show_hide_plugins(self):
        self.send_keys("^%p")

    def show_plugins(self):
        self.send_keys("^{F1}")

    def hide_plugins(self):
        self.send_keys("^{F2}")

    def toggle_device_button(self, x, y, activate=True):
        # type: (int, int) -> None
        subprocess.Popen(["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
                          home + "\\Google Drive\\music\\dev\\scripts\\ahk\\deactivate_ableton_button.ahk",
                          str(x), str(y), "1" if activate else "0"]).communicate()

    def is_plugin_window_visible(self, plugin_name=""):
        # type: (str) -> bool
        child = subprocess.Popen(["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
                                  home + "\\Google Drive\\music\\dev\\scripts\\ahk\\show_plugins_and_check.ahk",
                                  str(plugin_name)])
        child.communicate()
        return bool(child.returncode)

    def show_and_activate_rev2_editor(self):
        self.send_keys("^{F3}")

    @defer
    def group_track(self):
        self.send_keys("^{F4}")

    def up(self):
        self.send_keys("^{F5}")

    def duplicate(self):
        self.send_keys("^d")
