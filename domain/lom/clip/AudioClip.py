from functools import partial

import Live
from typing import Any, Optional, List

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.shared.Config import Config
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        Scheduler.defer(self.appearance.refresh)

        # associate the clip with a midi content
        self.previous_file_path = None  # type: Optional[str]

        if self.name == Config.DUMMY_CLIP_NAME:
            Scheduler.defer(self.config_dummy_clip)

    def get_hash(self, device_parameters):
        # type: (List[DeviceParameter]) -> int
        return hash((self.file_path, self.automation.get_hash(device_parameters)))

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
        self.color = ColorEnum.FOCUSED.value

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

    def config_dummy_clip(self):
        # type: () -> None
        self._clip.warping = True

        self.looping = True
        scene = Song.scenes()[self.index]
        self.bar_length = scene.bar_length

        self.clip_name.update("")

        ApplicationView.show_clip()
        self.show_loop()
