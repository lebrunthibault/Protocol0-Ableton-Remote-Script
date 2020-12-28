import sys

import win32api
import win32com.client
import win32con


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


shell = win32com.client.Dispatch("WScript.Shell")

if __name__ == "__main__":
    x, y = sys.argv[1].split(",")
    click(int(x), int(y))
