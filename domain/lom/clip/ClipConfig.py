class ClipConfig(object):
    def __init__(self, color=1, uses_scene_length_clips=False, default_note=0):
        # type: (int, bool, int) -> None
        self._color = color
        self.uses_scene_length_clips = uses_scene_length_clips
        self.default_note = default_note

    @property
    def color(self):
        # type: () -> int
        return self._color
