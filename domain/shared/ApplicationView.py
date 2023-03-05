import Live
from typing import Optional

from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.shared.SessionServiceInterface import SessionServiceInterface
from protocol0.shared.Song import Song


class ApplicationView(object):
    """Facade for accessing the application view"""

    _INSTANCE = None  # type: Optional[ApplicationView]

    def __init__(self, recording_component, application_view, session_service):
        # type: (RecordingComponent, Live.Application.Application.View, SessionServiceInterface) -> None
        ApplicationView._INSTANCE = self
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
        """Shows track view."""
        cls._INSTANCE._application_view.show_view("Detail")
        cls._INSTANCE._application_view.show_view("Detail/DeviceChain")

    @classmethod
    def show_session(cls):
        # type: () -> None
        cls._INSTANCE._application_view.show_view("Session")

    @classmethod
    def show_arrangement(cls):
        # type: () -> None
        cls._INSTANCE._application_view.show_view("Arranger")
        cls._INSTANCE._recording_component.back_to_arranger = False

    @classmethod
    def show_browser(cls):
        # type: () -> None
        cls._INSTANCE._application_view.show_view("Browser")

    @classmethod
    def focus_detail(cls):
        # type: () -> None
        cls._focus_view("Detail")

    @classmethod
    def focus_session(cls):
        # type: () -> None
        cls._focus_view("Session")

    @classmethod
    def focus_current_track(cls):
        # type: () -> None
        """Moves the focus to the detail view."""
        selected_track = Song.selected_track()
        is_visible = Song.selected_track().is_visible
        if Song.selected_track().group_track:
            Song.selected_track().group_track.is_folded = False
            # NB : unfolding parent classes will select them
            if Song.selected_track() != selected_track:
                selected_track.select()

            if not is_visible:
                # careful: this will impact the session display for long sets (scroll it up or down)
                cls._INSTANCE._session_service.toggle_session_ring()

    @classmethod
    def _focus_view(cls, view):
        # type: (str) -> None
        """Moves the focus to the given view, showing it first if needed."""
        if not cls._INSTANCE._application_view.is_view_visible(view):
            cls._INSTANCE._application_view.show_view(view)
        cls._INSTANCE._application_view.focus_view(view)

    @classmethod
    def is_session_visible(cls):
        # type: () -> bool
        return cls._INSTANCE._application_view.is_view_visible("Session")

    @classmethod
    def is_clip_view_visible(cls):
        # type: () -> bool
        return cls._INSTANCE._application_view.is_view_visible("Detail/Clip")

    @classmethod
    def is_browser_visible(cls):
        # type: () -> bool
        return cls._INSTANCE._application_view.is_view_visible("Browser")

    @classmethod
    def toggle_browse(cls):
        # type: () -> bool
        return cls._INSTANCE._application_view.toggle_browse()
