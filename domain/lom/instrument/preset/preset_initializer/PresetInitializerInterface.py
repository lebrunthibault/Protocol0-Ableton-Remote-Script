from typing import List, Optional, TYPE_CHECKING

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class PresetInitializerInterface(object):
    def __init__(self, device, track):
        # type: (Optional[Device], SimpleTrack) -> None
        """ Fetches the selected preset from the device or track """
        self._device = device
        self._track = track

    def get_selected_preset(self, presets):
        # type: (List[InstrumentPreset]) -> Optional[InstrumentPreset]
        raise NotImplementedError
