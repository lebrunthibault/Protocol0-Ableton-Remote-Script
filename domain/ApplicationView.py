from typing import Optional

import Live


# noinspection PyArgumentList
class ApplicationView(object):
    """ Facade for accessing the application view """

    _APPLICATION_VIEW = None  # type: Optional[Live.Application.Application.View]

    @classmethod
    def _application_view(cls):
        # type: () -> Live.Application.Application.View
        if not cls._APPLICATION_VIEW:
            from protocol0 import Protocol0

            cls._APPLICATION_VIEW = Protocol0.APPLICATION.view
        return cls._APPLICATION_VIEW

    @classmethod
    def show_clip(cls):
        # type: () -> None
        if not cls._application_view().is_view_visible("Detail/Clip"):
            cls._application_view().show_view("Detail")
            cls._application_view().show_view("Detail/Clip")

    @classmethod
    def show_device(cls):
        # type: () -> None
        """ Shows track view. """
        cls._application_view().show_view('Detail')
        cls._application_view().show_view('Detail/DeviceChain')

    @classmethod
    def show_session(cls):
        # type: () -> None
        cls._application_view().show_view('Session')

    @classmethod
    def show_arrangement(cls):
        # type: () -> None
        cls._application_view().show_view('Arranger')

    @classmethod
    def focus_detail(cls):
        # type: () -> None
        """ Moves the focus to the detail view. """
        cls._focus_view("Detail")

    @classmethod
    def _focus_view(cls, view):
        # type: (str) -> None
        """ Moves the focus to the given view, showing it first if needed. """
        if not cls._application_view().is_view_visible(view):
            cls._application_view().show_view(view)
        cls._application_view().focus_view(view)

    @classmethod
    def is_session_view_active(cls):
        # type: () -> bool
        return cls._application_view().is_view_visible('Session')
