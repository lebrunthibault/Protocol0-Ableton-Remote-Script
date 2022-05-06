import Live
from typing import Optional, Callable

from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.shared.SessionServiceInterface import SessionServiceInterface
from protocol0.shared.SongFacade import SongFacade


# noinspection PyArgumentList
class ApplicationViewFacade(object):
    """ Facade for accessing the application view """

    _INSTANCE = None  # type: Optional[ApplicationViewFacade]

    def __init__(self, recording_component, select_track, application_view, session_service):
        # type: (RecordingComponent, Callable, Live.Application.Application.View, SessionServiceInterface) -> None
        ApplicationViewFacade._INSTANCE = self
        self._select_track = select_track
        self._recording_component = recording_component
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
    def toggle_session_arrangement(cls):
        # type: () -> None
        if not cls.is_session_visible():
            cls.show_session()
        else:
            cls.show_arrangement()

    @classmethod
    def show_session(cls):
        # type: () -> None
        cls._INSTANCE._application_view.show_view('Session')

    @classmethod
    def show_arrangement(cls):
        # type: () -> None
        cls._INSTANCE._application_view.show_view('Arranger')
        cls._INSTANCE._recording_component.back_to_arranger = False

    @classmethod
    def focus_detail(cls):
        # type: () -> None
        """ Moves the focus to the detail view. """
        cls._focus_view("Detail")

    @classmethod
    def focus_current_track(cls):
        # type: () -> None
        """ Moves the focus to the detail view. """
        selected_track = SongFacade.selected_track()
        if SongFacade.selected_track().group_track \
                and any(t.is_folded for t in SongFacade.selected_track().group_tracks):
            SongFacade.selected_track().group_track.is_folded = False
            # NB : unfolding parent classes will select them
            if SongFacade.selected_track() != selected_track:
                cls._INSTANCE._select_track(selected_track)

            if not SongFacade.selected_track().is_visible:
                # careful: this will impact the session display for long sets (scroll it up or down)
                cls._INSTANCE._session_service.toggle_session_ring()

    @classmethod
    def _focus_view(cls, view):
        # type: (str) -> None
        """ Moves the focus to the given view, showing it first if needed. """
        if not cls._INSTANCE._application_view.is_view_visible(view):
            cls._INSTANCE._application_view.show_view(view)
        cls._INSTANCE._application_view.focus_view(view)

    @classmethod
    def is_session_visible(cls):
        # type: () -> bool
        return cls._INSTANCE._application_view.is_view_visible('Session')

    @classmethod
    def toggle_browse(cls):
        # type: () -> bool
        return cls._INSTANCE._application_view.toggle_browse()
