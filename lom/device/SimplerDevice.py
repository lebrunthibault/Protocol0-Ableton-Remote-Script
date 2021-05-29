import os
from os.path import basename

import Live
from typing import Any, Optional

from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceType import DeviceType


class SimplerDevice(Device):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimplerDevice, self).__init__(*a, **k)
        self._device = self._device  # type: Live.SimplerDevice.SimplerDevice
        self.device_type = DeviceType.ABLETON_DEVICE

    @property
    def sample_name(self):
        # type: () -> Optional[str]
        # noinspection PyBroadException
        try:
            sample = self._device.sample
        except Exception:
            # can happen while loading a new sample
            return None
        if sample:
            return os.path.splitext(basename(sample.file_path))[0]
        else:
            return None
