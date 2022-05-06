class ClipConfig(object):
    def __init__(self, index, color=1, uses_scene_length_clips=False, default_note=0):
        # type: (int, int, bool, int) -> None
        self.color = color
        self.uses_scene_length_clips = uses_scene_length_clips
        self.default_note = default_note
        self.index = index
