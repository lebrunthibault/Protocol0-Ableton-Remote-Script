import os
from os.path import basename

import Live
from typing import Any

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
        # type: () -> str
        return os.path.splitext(basename(self._device.sample.file_path))[0]
