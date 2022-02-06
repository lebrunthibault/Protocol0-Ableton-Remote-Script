import os

from typing import Any

import Live
from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.shared.SongFacade import SongFacade


class InstrumentSimpler(InstrumentInterface):
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
        # type: (InstrumentPreset) -> None
        SongFacade.selected_track.device_insert_mode = Live.Track.DeviceInsertMode.default
        self.parent.browserManager.load_sample(preset.original_name)  # type: ignore[arg-type]
