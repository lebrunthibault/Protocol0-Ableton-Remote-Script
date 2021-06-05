# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import requests
from utils.log import log
from utils.window import focus_ableton


def send_search(search):
    # type: (str) -> None
    log("sending search %s to server" % search)
    requests.get("http://127.0.0.1:8000/search/%s" % search, auth=("user", "pass"))


def create_gui():
    # type: () -> None
    layout = [[sg.Input(key="input")]]
    window = sg.Window("", layout, return_keyboard_events=True, no_titlebar=True)

    while True:
        event, values = window.read()
        if event.split(":")[0] == "Escape":
            log("Escape pressed, exiting")
            break

        if len(event) == 1 and ord(event) == 13:
            log("Enter pressed, clearing and focusing ableton")
            window["input"].update("")
            focus_ableton()
            continue

        if len(event) == 1:
            search = values["input"]
            if len(search) >= 3:
                send_search(search)

    window.close()


if __name__ == "__main__":
    create_gui()
