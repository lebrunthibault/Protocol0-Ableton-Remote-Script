import subprocess
from os.path import expanduser

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent

home = expanduser("~")


class AhkManager(AbstractControlSurfaceComponent):
    def _sendKeys(self, keys):
        # type: (str) -> None
        self.parent.log_info("Sending keys to ahk : " + keys)
        subprocess.Popen(["pythonw.exe",
                          home + "\\Google Drive\\music\\dev\\scripts\\python\\sendKeys.py",
                          keys]
                         ).communicate()

    def toggle_first_vst(self):
        # type: () -> None
        self._sendKeys("^{F1}")

    def toggle_first_vst_with_rack(self):
        # type: () -> None
        self._sendKeys("^{F2}")

    def show_and_activate_rev2_editor(self):
        # type: () -> None
        self._sendKeys("^{F3}")
