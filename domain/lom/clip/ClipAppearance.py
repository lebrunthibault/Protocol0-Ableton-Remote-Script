import Live

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip.ClipName import ClipName


class ClipAppearance(object):
    def __init__(self, live_clip, clip_name, color):
        # type: (Live.Clip.Clip, ClipName, int) -> None
        self._live_clip = live_clip
        self._clip_name = clip_name
        self._color = color

    @property
    def name(self):
        # type: () -> str
        if self._live_clip:
            return self._live_clip.name
        else:
            return ""

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._live_clip and name:
            self._live_clip.name = str(name).strip()

    @property
    def color(self):
        # type: () -> int
        return self._live_clip.color_index if self._live_clip else 0

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        if self._live_clip:
            self._live_clip.color_index = color_index

    def refresh(self):
        # type: () -> None
        self._clip_name._name_listener(force=True)
        if self.color != ClipColorEnum.AUDIO_UN_QUANTIZED.color_int_value:
            self.color = self._color