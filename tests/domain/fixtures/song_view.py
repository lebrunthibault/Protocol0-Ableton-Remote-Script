from _Framework.SubjectSlot import Subject
from typing import Optional

from protocol0.tests.domain.fixtures.simple_track import AbletonTrack


class AbletonSongView(Subject):
    __subject_events__ = ("selected_track", "selected_scene", "detail_clip")

    def __init__(self):
        # type: (Optional[AbletonTrack]) -> None
        self.selected_track = None
        self.selected_scene = None
