from _Framework.SubjectSlot import Subject

from protocol0.tests.domain.fixtures.clip_view import AbletonClipView


class AbletonClip(Subject):
    __subject_events__ = (
        "playing_status",
        "loop_start",
        "loop_end",
        "looping",
        "start_marker",
        "end_marker",
        "name",
        "warping",
        "muted",
    )

    def __init__(self):
        self.name = "test"
        self.view = AbletonClipView()
        self.is_recording = False
        self.length = 4
        self.color_index = 0
        self.looping = True
        self.loop_start = 0
        self.loop_end = 4
        self.muted = False
        self.playing_position = 0
        self.start_marker = 0
        self.is_audio_clip = False
        self.is_playing = False

    # noinspection PyUnusedLocal
    def get_notes_extended(self, *a, **k):
        return ()

    def select_all_notes(self):
        pass

    def replace_selected_notes(self, _):
        pass
