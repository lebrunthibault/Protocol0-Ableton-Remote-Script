from _Framework.SessionComponent import SessionComponent
from typing import Optional, Callable

from protocol0.domain.lom.clip.ClipCreatedEvent import ClipCreatedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.SessionServiceInterface import SessionServiceInterface
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.SongFacade import SongFacade


class SessionService(SessionServiceInterface):
    def __init__(self, component_guard, set_highlighting_session_component):
        # type: (Callable, Callable) -> None
        super(SessionService, self).__init__()
        self._component_guard = component_guard
        self._set_highlighting_session_component = set_highlighting_session_component
        self._session = None  # type: Optional[SessionComponent]
        DomainEventBus.subscribe(ClipCreatedEvent, lambda _: self._emit_session_updated_event())

    def _emit_session_updated_event(self):
        # type: () -> None
        DomainEventBus.notify(SessionUpdatedEvent())

    def toggle_session_ring(self):
        # type: () -> None
        self._display_session_ring()
        self._hide_session_ring()

    def _display_session_ring(self):
        # type: () -> None
        if self._session:
            self._hide_session_ring()

        try:
            if not SongFacade.selected_track().IS_ACTIVE:
                return
        except IndexError:
            return

        total_tracks = SongFacade.current_track().get_all_simple_sub_tracks()
        num_tracks = len([track for track in total_tracks if track.is_visible])
        track_offset = self._session_track_offset

        with self._component_guard():
            self._session = SessionComponent(num_tracks=num_tracks, num_scenes=len(SongFacade.scenes()))
        self._session.set_offsets(track_offset=track_offset, scene_offset=0)
        if track_offset != len(list(SongFacade.visible_tracks())) - 1:
            self._set_highlighting_session_component(self._session)

    def _hide_session_ring(self):
        # type: () -> None
        if self._session:
            self._session.set_show_highlight(False)
            self._session.disconnect()

    @property
    def _session_track_offset(self):
        # type: () -> int
        try:
            return list(SongFacade.visible_tracks()).index(SongFacade.current_track().base_track)
        except ValueError:
            return self._session.track_offset() if self._session else 0
