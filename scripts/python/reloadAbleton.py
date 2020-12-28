import time
import win32com.client
import win32gui

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