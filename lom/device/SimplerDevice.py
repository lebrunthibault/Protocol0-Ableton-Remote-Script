import os
from os.path import basename

import Live
from typing import Any, Optional

from protocol0.lom.device.Device import Device
from protocol0.lom.device.DeviceType import DeviceType
from protocol0.utils.utils import smart_string


class SimplerDevice(Device):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimplerDevice, self).__init__(*a, **k)
        self._device = self._device  # type: Live.SimplerDevice.SimplerDevice
        self.device_type = DeviceType.ABLETON_DEVICE

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
