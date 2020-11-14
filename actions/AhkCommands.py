from os.path import expanduser
import subprocess

from ClyphX_Pro.clyphx_pro.user_actions.utils.log import log

home = expanduser("~")


class AhkCommands(object):
    def __init__(self):
        pass

    @classmethod
    def sendKeys(cls, keys):
        # type: (str) -> None
        log("Sending keys to ahk : " + keys)
        subprocess.Popen(["pythonw.exe",
                          home + "\\Google Drive\\music\\dev\\scripts\\python\\sendKeys.py",
                          keys]
                         ).communicate()

    @classmethod
    def select_first_vst(cls):
        # type: () -> None
        AhkCommands.sendKeys("^{F1}")

    @classmethod
    def show_and_activate_rev2_editor(cls):
        # type: () -> None
        AhkCommands.sendKeys("^{F3}")

