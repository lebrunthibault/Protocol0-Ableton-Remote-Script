from typing import Optional

from _Framework.SubjectSlot import Subject
from protocol0.tests.fixtures.simple_track import AbletonTrack


class AbletonSongView(Subject):
    def __init__(self, selected_track=None):
        # type: (Optional[AbletonTrack]) -> None
        self.selected_track = selected_track
