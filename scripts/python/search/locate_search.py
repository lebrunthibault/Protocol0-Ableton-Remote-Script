import subprocess

import win32gui
from search_set import create_gui
from utils import setup_logs, log, find_search_window_handle

from a_protocol_0.consts import SERVER_DIR


def display_search():
    # type: () -> None
    search_window_handle = find_search_window_handle(class_name="TkTopLevel", app_name="python.exe")
    if search_window_handle:
        log("found search set window, focusing")
        win32gui.SetForegroundWindow(search_window_handle)
    else:
        log("didn't find search set window, creating gui")
        create_gui()
        subprocess.Popen([SERVER_DIR + "\\gui\\protocol0_search.bat"], shell=True)
        # KeyBoardShortcutManager.execute_batch(SERVER_DIR + "\\gui\\protocol0_search.bat")


if __name__ == "__main__":
    setup_logs()
    log("locating search set window")
    display_search()
