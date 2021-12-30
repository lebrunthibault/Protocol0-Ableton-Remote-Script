from typing import Optional

from _Framework.SubjectSlot import Subject
from protocol0.tests.fixtures.simple_track import AbletonTrack


class AbletonSongView(Subject):
    def __init__(self):
        # type: (Optional[AbletonTrack]) -> None
        self.selected_track = None
