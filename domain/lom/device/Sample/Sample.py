import os

import Live

from protocol0.domain.shared.utils.string import smart_string


class Sample(object):
    def __init__(self, sample):
        # type: (Live.Sample.Sample) -> None
        self._sample = sample

    def __repr__(self):
        # type: () -> str
        return "Sample(name='%s')" % self.name

    @property
    def name(self):
        # type: () -> str
        return str(os.path.splitext(os.path.basename(smart_string(self.file_path)))[0])

    @property
    def length(self):
        # type: () -> float
        return self._sample.length

    @property
    def file_path(self):
        # type: () -> str
        if self._sample:
            return self._sample.file_path
        else:
            return ""

    @property
    def warping(self):
        # type: () -> bool
        return self._sample.warping

    @warping.setter
    def warping(self, warping):
        # type: (bool) -> None
        self._sample.warping = warping

    @property
    def warp_mode(self):
        # type: () -> Live.Clip.WarpMode
        return self._sample.warp_mode

    @warp_mode.setter
    def warp_mode(self, warp_mode):
        # type: (Live.Clip.WarpMode) -> None
        self._sample.warp_mode = warp_mode

    def beat_to_sample_time(self, beat_time):
        # type: (float) -> float
        return self._sample.beat_to_sample_time(beat_time)
