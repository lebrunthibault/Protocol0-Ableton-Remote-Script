from typing import Optional, Any

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.sequence.Sequence import Sequence


class BrowserServiceInterface(object):
    def load_device_from_enum(self, device_enum):
        # type: (DeviceEnum) -> Sequence
        raise NotImplementedError

    def load_sample(self, sample_name, **k):
        # type: (str, Any) -> None
        raise NotImplementedError

    def update_audio_effect_preset(self, device):
        # type: (Device) -> Optional[Sequence]
        raise NotImplementedError
