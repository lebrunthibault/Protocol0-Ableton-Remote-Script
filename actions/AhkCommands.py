import subprocess
from os.path import expanduser
from typing import TYPE_CHECKING

from _Framework.Dependency import depends

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0 import Protocol0Component

home = expanduser("~")


class AhkCommands(object):
    @depends(parent=None)
    def __init__(self, parent=None):
        # type: ("Protocol0Component") -> None
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

    def toggle_first_vst_with_rack(self):
        # type: () -> None
        self._sendKeys("^{F2}")

    def show_and_activate_rev2_editor(self):
        # type: () -> None
        self._sendKeys("^{F3}")
