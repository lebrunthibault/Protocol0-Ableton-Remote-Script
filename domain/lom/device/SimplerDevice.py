import os
from os.path import basename

from typing import Any, Optional

import Live
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.shared.utils import smart_string


class SimplerDevice(Device):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimplerDevice, self).__init__(*a, **k)
        self._device = self._device  # type: Live.SimplerDevice.SimplerDevice

    @property
    def preset_name(self):
        # type: () -> Optional[str]
        """ overridden """
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
