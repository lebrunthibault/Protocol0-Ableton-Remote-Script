from functools import partial

import Live
from typing import Any, Optional, Dict

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.shared.sequence.Sequence import Sequence


class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        Scheduler.defer(self.appearance.refresh)

        # associate the clip with a midi content
        self.midi_hash = None  # type: Optional[int]
        self.previous_file_path = None  # type: Optional[str]

    def to_dict(self):
        # type: () -> Dict
        return {
            "index": self.index,
            "midi_hash": self.midi_hash,
            "file_path": self.file_path
        }

    def update_from_dict(self, clip_data):
        # type: (Dict) -> None
        self.midi_hash = clip_data["midi_hash"]

    def matches(self, other):
        # type: (AudioClip) -> bool
        return self.loop.matches(other.loop) and self.file_path == other.file_path

    @property
    def warp_mode(self):
        # type: () -> Live.Clip.WarpMode
        return self._clip.warp_mode

    @warp_mode.setter
    def warp_mode(self, warp_mode):
        # type: (Live.Clip.WarpMode) -> None
        self._clip.warp_mode = warp_mode

    @property
    def file_path(self):
        # type: () -> str
        return self._clip.file_path if self._clip else ""

    def focus(self):
        # type: () -> None
        self.color = ColorEnum.FOCUSED.int_value

    def crop(self):
        # type: () -> Optional[Sequence]
        self.loop.fix()

        clip_color = self.color

        seq = Sequence()
        seq.defer()
        seq.add(self.focus)
        seq.defer()
        seq.add(Backend.client().crop_clip)
        seq.wait_for_backend_event("clip_cropped")
        seq.add(partial(setattr, self, "color", clip_color))
        return seq.done()
