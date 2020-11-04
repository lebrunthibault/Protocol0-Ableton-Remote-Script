from typing import Optional

from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.simpleTrack import AbletonTrack


class AbletonSongView:
    def __init__(self, selected_track=None):
        # type: (Optional[AbletonTrack]) -> None
        self.selected_track = selected_track
