from _Framework.SubjectSlot import Subject

from protocol0.tests.domain.fixtures.clip_view import AbletonClipView


class AbletonClip(Subject):
    __subject_events__ = (
        "playing_status",
        "loop_start",
        "loop_end",
        "start_marker",
        "end_marker",
        "name",
        "warping",
        "muted"
    )

    def __init__(self):
        self.name = "test"
        self.view = AbletonClipView()
        self.is_recording = False
        self.length = 4
        self.color_index = 0
        self.loop_start = 0
        self.muted = False
        self.playing_position = 0
        self.start_marker = 0

    # noinspection PyUnusedLocal
    def get_notes(self, *a, **k):
        return ()
