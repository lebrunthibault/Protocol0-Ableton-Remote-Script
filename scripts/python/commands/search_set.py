import logging

import PySimpleGUI as sg
import requests
import win32gui

from lib.window.find_window import find_window_handle_by_criteria
from lib.window.window import focus_ableton

KEEP_WINDOW_IN_BACKGROUND = False


def send_search(search):
    # type: (str) -> None
    logging.info("sending search %s to server" % search)
    requests.get("http://127.0.0.1:8000/search/%s" % search, auth=("user", "pass"))


def create_gui():
    # type: () -> None
    layout = [[sg.Input(key="input")]]
    window = sg.Window("", layout, return_keyboard_events=True, no_titlebar=True)

    while True:
        event, values = window.read()
        if event.split(":")[0] == "Escape":
            logging.info("Escape pressed, exiting")
            break

        if len(event) == 1 and ord(event) == 13:
            if KEEP_WINDOW_IN_BACKGROUND:
                logging.info("Enter pressed, clearing and focusing ableton")
                window["input"].update("")
                focus_ableton()
                continue
            else:
                logging.info("Enter pressed, closing")
                break

        if len(event) == 1:
            search = values["input"]
            if len(search) >= 3:
                send_search(search)

    window.close()


def search_set():
    # type: () -> None
    search_window_handle = find_window_handle_by_criteria(class_name="TkTopLevel", app_name="python.exe")
    if search_window_handle:
        logging.info("found search set window, focusing")
        win32gui.SetForegroundWindow(search_window_handle)
    else:
        logging.info("didn't find search set window, creating gui")
        create_gui()


if __name__ == "__main__":
    search_set()
