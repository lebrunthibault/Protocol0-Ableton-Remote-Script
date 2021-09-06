from typing import Optional, Any, List

from _Framework.SessionComponent import SessionComponent
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.utils.decorators import defer


class SessionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SessionManager, self).__init__(*a, **k)
        self.session = None  # type: Optional[SessionComponent]
        self.register_slot(self.parent.songManager, self._setup_session_control, "selected_track")

    def _setup_session_control(self):
        # type: () -> None
        if self.session:
            self.session.set_show_highlight(False)
            self.session.disconnect()

        try:
            if not self.song.selected_track.is_active:
                return
        except IndexError:
            return

        def get_all_sub_tracks_inclusive(track):
            # type: (SimpleTrack) -> List[SimpleTrack]
            sub_tracks = [track]
            for sub_track in track.sub_tracks:
                sub_tracks.extend(get_all_sub_tracks_inclusive(sub_track))
            return sub_tracks

        total_tracks = get_all_sub_tracks_inclusive(self.song.current_track.base_track)
        num_tracks = len([track for track in total_tracks if track.is_visible])

        with self.parent.component_guard():
            self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(self.song.scenes))
        self.session.set_offsets(track_offset=self.session_track_offset, scene_offset=0)
        self.parent.set_highlighting_session_component(self.session)

    @property
    def session_track_offset(self):
        # type: () -> int
        try:
            return [t for t in self.song.simple_tracks if t.is_visible].index(self.song.current_track.base_track)
        except ValueError:
            return self.session.track_offset() if self.session else 0
