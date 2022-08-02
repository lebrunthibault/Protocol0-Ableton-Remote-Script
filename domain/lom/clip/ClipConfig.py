class ClipConfig(object):
    def __init__(self, color=1, default_note=0):
        # type: (int, int) -> None
        self._color = color
        self.default_note = default_note

    @property
    def color(self):
        # type: () -> int
        return self._color
