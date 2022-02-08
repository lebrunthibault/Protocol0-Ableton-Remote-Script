from typing import Optional

import Live
from protocol0.domain.shared.SessionServiceInterface import SessionServiceInterface


# noinspection PyArgumentList
class ApplicationView(object):
    """ Facade for accessing the application view """

    _INSTANCE = None  # type: Optional[ApplicationView]

    def __init__(self, application_view, session_service):
        # type: (Live.Application.Application.View, SessionServiceInterface) -> None
        ApplicationView._INSTANCE = self
        self._application_view = application_view
        self._session_service = session_service

    @classmethod
    def show_clip(cls):
        # type: () -> None
        if not cls._INSTANCE._application_view.is_view_visible("Detail/Clip"):
            cls._INSTANCE._application_view.show_view("Detail")
            cls._INSTANCE._application_view.show_view("Detail/Clip")

    @classmethod
    def show_device(cls):
        # type: () -> None
        """ Shows track view. """
        cls._INSTANCE._application_view.show_view('Detail')
        cls._INSTANCE._application_view.show_view('Detail/DeviceChain')

    @classmethod
    def show_session(cls):
        # type: () -> None
        cls._INSTANCE._application_view.show_view('Session')

    @classmethod
    def show_arrangement(cls):
        # type: () -> None
        cls._INSTANCE._application_view.show_view('Arranger')

    @classmethod
    def focus_detail(cls):
        # type: () -> None
        """ Moves the focus to the detail view. """
        cls._focus_view("Detail")

    @classmethod
    def focus_current_track(cls):
        # type: () -> None
        """ Moves the focus to the detail view. """
        cls._INSTANCE._session_service.toggle_session_ring()

    @classmethod
    def _focus_view(cls, view):
        # type: (str) -> None
        """ Moves the focus to the given view, showing it first if needed. """
        if not cls._INSTANCE._application_view.is_view_visible(view):
            cls._INSTANCE._application_view.show_view(view)
        cls._INSTANCE._application_view.focus_view(view)

    @classmethod
    def is_session_view_active(cls):
        # type: () -> bool
        return cls._INSTANCE._application_view.is_view_visible('Session')
