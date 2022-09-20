from typing import List

from protocol0.domain.lom.device.DrumPad import DrumPad
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.shared.logging.Logger import Logger


class DrumRackDevice(RackDevice):
    def pad_names_equal(self, names):
        # type: (List[str]) -> bool
        pad_names = [drum_pad.name for drum_pad in self.filled_drum_pads]
        if names != pad_names:
            Logger.info("difference: %s" % list(set(names) - set(pad_names)))
        return names == pad_names

    @property
    def drum_pads(self):
        # type: () -> List[DrumPad]
        return [DrumPad(drum_pad) for drum_pad in self._device.drum_pads if drum_pad]

    @property
    def filled_drum_pads(self):
        # type: () -> List[DrumPad]
        return [drum_pad for drum_pad in self.drum_pads if not drum_pad.is_empty]

    @property
    def selected_drum_pad(self):
        # type: () -> DrumPad
        return DrumPad(self._device.view.selected_drum_pad)

    @selected_drum_pad.setter
    def selected_drum_pad(self, drum_pad):
        # type: (DrumPad) -> None
        self._device.view.selected_drum_pad = drum_pad._drum_pad
