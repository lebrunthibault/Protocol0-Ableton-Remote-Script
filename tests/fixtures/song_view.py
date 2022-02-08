from typing import Optional

from _Framework.SubjectSlot import Subject
from protocol0.tests.fixtures.scene import AbletonScene
from protocol0.tests.fixtures.simple_track import AbletonTrack


class AbletonSongView(Subject):
    __subject_events__ = ("selected_track", "selected_scene")

    def __init__(self):
        # type: (Optional[AbletonTrack]) -> None
        self.selected_track = AbletonTrack()
        self.selected_scene = AbletonScene()
