from typing import Optional, List, Callable

from _Framework.SessionComponent import SessionComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.SessionServiceInterface import SessionServiceInterface
from protocol0.shared.SongFacade import SongFacade


class SessionService(SessionServiceInterface):
    def __init__(self, component_guard, set_highlighting_session_component):
        # type: (Callable, Callable) -> None
        super(SessionService, self).__init__()
        self._component_guard = component_guard
        self._set_highlighting_session_component = set_highlighting_session_component
        self.session = None  # type: Optional[SessionComponent]

    def toggle_session_ring(self):
        # type: () -> None
        self._display_session_ring()
        self._hide_session_ring()

    def _display_session_ring(self):
        # type: () -> None
        if self.session:
            self._hide_session_ring()

        try:
            if not SongFacade.selected_track().IS_ACTIVE:
                return
        except IndexError:
            return

        def get_all_sub_tracks_inclusive(parent_track):
            # type: (SimpleTrack) -> List[SimpleTrack]
            sub_tracks = [parent_track]
            for sub_track in parent_track.sub_tracks:
                sub_tracks.extend(get_all_sub_tracks_inclusive(sub_track))
            return sub_tracks

        total_tracks = get_all_sub_tracks_inclusive(SongFacade.current_track().base_track)
        num_tracks = len([track for track in total_tracks if track.is_visible])
        track_offset = self._session_track_offset

        with self._component_guard():
            self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(SongFacade.scenes()))
        self.session.set_offsets(track_offset=track_offset, scene_offset=0)
        if track_offset != len(list(SongFacade.visible_tracks())) - 1:
            self._set_highlighting_session_component(self.session)

    def _hide_session_ring(self):
        # type: () -> None
        if self.session:
            self.session.set_show_highlight(False)
            self.session.disconnect()

    @property
    def _session_track_offset(self):
        # type: () -> int
        try:
            return list(SongFacade.visible_tracks()).index(SongFacade.current_track().base_track)
        except ValueError:
            return self.session.track_offset() if self.session else 0
