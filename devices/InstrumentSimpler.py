import os

from typing import Any, Optional

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.devices.presets.InstrumentPreset import InstrumentPreset
from protocol0.enums.ColorEnum import ColorEnum
from protocol0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.lom.device.SimplerDevice import SimplerDevice
from protocol0.sequence.Sequence import Sequence


class InstrumentSimpler(AbstractInstrument):
    NAME = "Simpler"
    TRACK_COLOR = ColorEnum.SIMPLER
    PRESET_EXTENSION = ".wav"
    PRESETS_PATH = str(os.getenv("SAMPLE_PATH"))
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.CATEGORY
    CAN_BE_SHOWN = False

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.device = self.device  # type: SimplerDevice

    def load_preset(self, preset):
        # type: (InstrumentPreset) -> Optional[Sequence]
        import Live
        self.song.selected_track.device_insert_mode = Live.Track.DeviceInsertMode.default
        self.parent.browserManager.load_sample(preset.original_name)  # type: ignore[arg-type]
        # self.parent.wait(100, self.track._devices_listener)
        return None
