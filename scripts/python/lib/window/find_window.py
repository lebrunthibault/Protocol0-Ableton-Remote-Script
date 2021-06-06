import logging
from functools import partial
from typing import Optional, Any, List

import win32gui
import win32process
import wmi
from a_protocol_0.enums.AbstractEnum import AbstractEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error


class SearchTypeEnum(AbstractEnum):
    NAME = "NAME"
    EXE = "EXE"
    CLASS = "CLASS"


def find_window_handle_by_enum(name: str, search_type: SearchTypeEnum) -> int:
    if search_type == SearchTypeEnum.NAME:
        find_func = partial(find_window_handle_by_criteria, partial_name=name)
    elif search_type == SearchTypeEnum.EXE:
        find_func = partial(find_window_handle_by_criteria, app_name=name)
    elif search_type == SearchTypeEnum.CLASS:
        find_func = partial(find_window_handle_by_criteria, class_name=name)
    else:
        raise Protocol0Error("Invalid enum value %s" % search_type)

    return find_func()


def find_window_handle_by_criteria(class_name: Optional[str] = None, app_name: Optional[str] = None,
                                   partial_name: Optional[str] = None) -> Optional[int]:
    assert class_name or app_name or partial_name, "You should give a criteria to search a window"

    handle = None

    def winEnumHandler(hwnd, _):
        # type: (int, Any) -> None
        nonlocal handle
        if (
                win32gui.IsWindowVisible(hwnd)
                and (not class_name or win32gui.GetClassName(hwnd) == class_name)
                and (not app_name or _get_app_name(hwnd) == app_name)
                and (not partial_name or partial_name in _get_window_title(hwnd))
        ):
            handle = hwnd

    win32gui.EnumWindows(winEnumHandler, None)

    if handle:
        logging.info("Window handle found : %s" % handle)
    else:
        logging.error("Window handle not found : %s" % handle)

    return handle


def show_windows(app_name_black_list: Optional[List[str]] = None, show_path=False) -> None:
    app_name_black_list = app_name_black_list or [
        "explorer.exe", "chrome.exe", "ipoint.exe", "TextInputHost.exe"
    ]

    def winEnumHandler(hwnd, _):
        # type: (int, Any) -> None
        if win32gui.IsWindowVisible(hwnd):
            name = _get_window_title(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            app_name = _get_app_name(hwnd)
            if app_name in app_name_black_list:
                return
            app_path = _get_app_path(hwnd)
            log = f"handle: {hwnd}, name: {name}, class_name: {class_name}, app_name: {app_name}"
            if show_path:
                log += f", app_path: {app_path}"
            logging.info(log)

    win32gui.EnumWindows(winEnumHandler, None)


def _get_window_title(hwnd: int) -> str:
    return win32gui.GetWindowText(hwnd)


def _get_app_path(hwnd: int) -> Optional[str]:
    """Get application path given hwnd."""
    # noinspection PyBroadException
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        c = wmi.WMI()
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        for p in c.query("SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            return p.ExecutablePath
    except Exception:
        return None


def _get_app_name(hwnd: int) -> Optional[str]:
    """Get application filename given hwnd."""
    # noinspection PyBroadException
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        c = wmi.WMI()

        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        for p in c.query("SELECT Name FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            return p.Name
    except Exception:
        return None
