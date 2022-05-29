import json

import Live
from typing import List, Any, Optional

from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0_push2.track_selection import SessionRingTrackProvider


class P0SessionRingTrackProvider(SessionRingTrackProvider):
    """
        Handling the push2 session ring

        Modifies which tracks are controlled by the session ring
        Session will now control and display only the scene tracks
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(P0SessionRingTrackProvider, self).__init__(*a, **k)
        self.set_enabled(False)
        DomainEventBus.subscribe(SelectedTrackChangedEvent, self._on_selected_track_changed_event)
        DomainEventBus.subscribe(SessionUpdatedEvent, self._on_session_updated_event)
        self._sync_session_to_selected_scene()
        self.track_offset = self.track_offset  # type: int

    def __repr__(self):
        # type: () -> str
        def live_track_to_string(track):
            # type: (Optional[Live.Track.Track]) -> str
            if track:
                return track.name
            else:
                return "None"

        try:
            data = {
                "selected_scene": str(SongFacade.selected_scene()),
                "tracks_to_use": [live_track_to_string(t._live_object) for t in self.tracks_to_use()],
                "num_tracks": self.num_tracks,
                "num_scenes": self.num_scenes,
                "scene_offset": self.scene_offset,
                "track_offset": self.track_offset,
                # "controlled_tracks": [live_track_to_string(t) for t in self.controlled_tracks()]
            }
            return "P0SessionRingTrackProvider(%s)" % json.dumps(data, indent=4)
        except AttributeError as e:
            return "(initializing..) -> %s" % e

    def _on_session_updated_event(self, _):
        # type: (SessionUpdatedEvent) -> None
        """Event to send so that the push2 session is updated"""
        self._update_track_list()
        self._sync_session_to_selected_scene()

    def _on_selected_track_changed_event(self, _):
        # type: (SelectedTrackChangedEvent) -> None
        """
            Rebuild session on selected track change.
            Useful because we want the selected track to be part of the push2 session
        """
        DomainEventBus.emit(SessionUpdatedEvent())

    def _sync_session_to_selected_scene(self):
        # type: () -> None
        self.scene_offset = SongFacade.selected_scene().index

    @property
    def session_tracks(self):
        # type: () -> List[AbstractTrack]
        """Only scene tracks + current tracks. Should be cached"""
        tracks = set(SongFacade.selected_scene().abstract_tracks)
        tracks.add(SongFacade.current_track())
        return sorted(tracks, key=lambda t: t.index)

    def tracks_to_use(self):
        # type: () -> List[Any]
        tracks = [t._track for t in self.session_tracks]
        return self._decorator_factory.decorate_all_mixer_tracks(tracks)

    def _ensure_valid_track_offset(self):
        # type: () -> None
        """Overriding to suppress error raising"""
        if len(self.tracks_to_use()):
            max_index = len(self.tracks_to_use()) - 1
        else:
            # return None
            max_index = 0
        clamped_offset = min(self.track_offset, max_index)
        if clamped_offset != self.track_offset:
            self.track_offset = clamped_offset
