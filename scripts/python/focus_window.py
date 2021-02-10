import sys

import win32gui

win32gui.SetForegroundWindow(win32gui.FindWindow(None, sys.argv[1]))
