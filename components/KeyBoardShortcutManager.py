import subprocess
from os.path import expanduser

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent

home = expanduser("~")


class KeyBoardShortcutManager(AbstractControlSurfaceComponent):
    def sendKeys(self, keys):
        # type: (str) -> None
        self.parent.log_info("Sending keys : " + keys)
        subprocess.Popen(["pythonw.exe",
                          home + "\\Google Drive\\music\\dev\\scripts\\python\\sendKeys.py",
                          keys]
                         ).communicate()

    def sendClick(self, x, y):
        # type: (int, int) -> None
        self.sendKeys("%d,%d" % (x, y))

    def show_hide_plugins(self):
        self.sendKeys("^%p")

    def toggle_first_vst(self):
        self.sendKeys("^{F1}")

    def toggle_first_vst_with_rack(self):
        self.sendKeys("^{F2}")

    def show_and_activate_rev2_editor(self):
        self.sendKeys("^{F3}")

    def group_track(self):
        self.sendKeys("^{F5}")

    def up(self):
        self.sendKeys("^{F6}")

