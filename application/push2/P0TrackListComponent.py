from protocol0_push2.track_list import TrackListComponent
from typing import Any

from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade


class P0TrackListComponent(TrackListComponent):
    def _select_mixable(self, track):
        # type: (Any) -> None
        """When clicking on a track selection button"""
        ApplicationViewFacade.show_device()
        return super(P0TrackListComponent, self)._select_mixable(track)
