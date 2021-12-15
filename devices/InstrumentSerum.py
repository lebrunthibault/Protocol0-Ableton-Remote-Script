from typing import Optional, Any

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.devices.presets.InstrumentPreset import InstrumentPreset
from protocol0.enums.ColorEnum import ColorEnum


class InstrumentSerum(AbstractInstrument):  # noqa
    NAME = "Serum"
    DEVICE_NAME = "serum_x64"
    TRACK_COLOR = ColorEnum.SERUM
    PRESETS_PATH = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"

    def make_preset(self, index, name=None, *_, **__):
        # type: (AbstractInstrument, int, Optional[str], Any, Any) -> InstrumentPreset
        """ overridden """
        category, preset_name = name.split("\\")
        return InstrumentPreset(instrument=self, index=index, name=preset_name, category=category)
