import time

import win32com
import win32com.client
import win32gui
from lib.window.find_window import SearchTypeEnum
from lib.window.window import focus_window


def reload_ableton() -> None:
    focus_window("Ableton Live Window Class", SearchTypeEnum.CLASS)
    win32gui.SetForegroundWindow(win32gui.FindWindow("Ableton Live Window Class", None))

    time.sleep(0.5)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys("^n")
    shell.SendKeys("{Right}")
    shell.SendKeys("{Right}")
    shell.SendKeys("{Right}")
    shell.SendKeys("{Right}")
    shell.SendKeys("{Enter}")
    shell.SendKeys("{Enter}")
