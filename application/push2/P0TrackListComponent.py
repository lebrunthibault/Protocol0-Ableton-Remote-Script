from protocol0_push2.track_list import TrackListComponent
from typing import Any

from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class P0TrackListComponent(TrackListComponent):
    def _select_mixable(self, track):
        # type: (Any) -> None
        """When clicking on a track selection button"""
        ApplicationViewFacade.show_device()
        Scheduler.defer(ApplicationViewFacade.focus_current_track)
        return super(P0TrackListComponent, self)._select_mixable(track)
