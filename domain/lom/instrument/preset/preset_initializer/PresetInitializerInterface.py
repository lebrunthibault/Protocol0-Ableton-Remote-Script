from typing import List, Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset


class PresetInitializerInterface(object):
    def __init__(self, device, track_name):
        # type: (Optional[Device], str) -> None
        """Fetches the selected preset from the device or track"""
        self._device = device
        self._track_name = track_name

    def get_selected_preset(self, presets):
        # type: (List[InstrumentPreset]) -> Optional[InstrumentPreset]
        raise NotImplementedError
