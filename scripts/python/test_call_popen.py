import os
import subprocess
from os.path import expanduser, dirname

PROTOCOL0_FOLDER = dirname(dirname(dirname(os.path.realpath(__file__))))
home = expanduser("~")

child = subprocess.Popen(["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
                          PROTOCOL0_FOLDER + "\\scripts\\ahk\\ableton_shortcuts.ahk"]
                         )
print(child.returncode)