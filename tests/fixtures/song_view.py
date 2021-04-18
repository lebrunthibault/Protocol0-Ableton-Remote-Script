from typing import Optional

from a_protocol_0.tests.fixtures.simpleTrack import AbletonTrack


class AbletonSongView(object):
    def __init__(self, selected_track=None):
        # type: (Optional[AbletonTrack]) -> None
        self.selected_track = selected_track
