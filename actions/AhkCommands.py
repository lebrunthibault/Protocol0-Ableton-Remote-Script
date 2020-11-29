from os.path import expanduser
import subprocess

from _Framework.Dependency import depends

home = expanduser("~")


class AhkCommands(object):
    @depends(parent=None)
    def __init__(self, parent=None, *a, **k):
        super(AhkCommands, self).__init__(*a, **k)
        self.parent = parent

    def _sendKeys(self, keys):
        # type: (str) -> None
        self.parent.log("Sending keys to ahk : " + keys)
        subprocess.Popen(["pythonw.exe",
                          home + "\\Google Drive\\music\\dev\\scripts\\python\\sendKeys.py",
                          keys]
                         ).communicate()

    def toggle_first_vst(self):
        # type: () -> None
        self._sendKeys("^{F1}")

    def show_and_activate_rev2_editor(self):
        # type: () -> None
        self._sendKeys("^{F2}")
