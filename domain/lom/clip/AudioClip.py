from functools import partial

import Live
from typing import Any, Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        Scheduler.defer(self.appearance.refresh)

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
        seq.log("done")
        seq.add(partial(setattr, self, "color", clip_color))
        return seq.done()

    def post_record(self, bar_length):
        # type: (int) -> None
        super(AudioClip, self).post_record(bar_length)
        from protocol0.shared.logging.Logger import Logger
        Logger.dev("audio clip")
        Logger.dev((bar_length, self.bar_length))
        Logger.dev((self.loop.end, self.loop.start + bar_length * SongFacade.signature_numerator()))
        if bar_length == self.bar_length:
            return

        if bar_length * 2 < self.bar_length:
            # we recorded twice
            self.loop.start = bar_length * SongFacade.signature_numerator()

        self.loop.end = self.loop.start + bar_length * SongFacade.signature_numerator()

