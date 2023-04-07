import os
from os.path import basename

import Live
from typing import Any, Optional, cast

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.Sample.Sample import Sample
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.string import smart_string


class SimplerDevice(Device):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimplerDevice, self).__init__(*a, **k)
        self._device = cast(
            Live.SimplerDevice.SimplerDevice, self._device
        )  # type: Live.SimplerDevice.SimplerDevice
        self._sample = Sample(self._device.sample)
        Scheduler.defer(self._set_warping)

    def __repr__(self):
        # type: () -> str
        return "SimplerDevice(name=%s, sample=%s)" % (self.name.encode('utf-8'), "test")

    @property
    def sample(self):
        # type: () -> Sample
        return self._sample

    @property
    def preset_name(self):
        # type: () -> Optional[str]
        """overridden"""
        # noinspection PyBroadException
        try:
            sample = self._device.sample
        except Exception:
            # can happen while loading a new sample
            return None
        if sample:
            return str(os.path.splitext(basename(smart_string(sample.file_path)))[0])
        else:
            return None

    def _set_warping(self):
        # type: () -> None
        if hasattr(self, "sample") and "loop" in self.sample.file_path.lower():
            self.sample.warping = True
            self._device.playback_mode = Live.SimplerDevice.PlaybackMode.classic
            release = self.get_parameter_by_name("Ve Release")
            release.value = 0.55  # 425 ms
