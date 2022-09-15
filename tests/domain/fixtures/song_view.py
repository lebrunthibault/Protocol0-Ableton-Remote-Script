from _Framework.SubjectSlot import Subject


class AbletonSongView(Subject):
    __subject_events__ = ("selected_track", "selected_scene", "selected_parameter", "detail_clip")

    def __init__(self):
        # type: () -> None
        self.selected_track = None
        self.selected_scene = None
