import sys

import win32api
import win32con


def click_and_restore_pos(x, y):
    (orig_x, orig_y) = win32api.GetCursorPos()
    click(x, y)
    win32api.SetCursorPos((orig_x, orig_y))


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


if __name__ == "__main__":
    click_and_restore_pos(int(sys.argv[1]), int(sys.argv[2]))
