from typing import Any

from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.shared.logging.Logger import Logger
from protocol0_push2.track_list import TrackListComponent


class P0TrackListComponent(TrackListComponent):
    def _select_mixable(self, track):
        # type: (Any) -> None
        Logger.dev("select mixable !")
        ApplicationViewFacade.show_device()
        return super(P0TrackListComponent, self)._select_mixable(track)
