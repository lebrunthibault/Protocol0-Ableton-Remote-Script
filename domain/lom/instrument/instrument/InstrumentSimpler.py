from typing import cast, Any

from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.preset_changer.SamplePresetChanger import (
    SamplePresetChanger,
)
from protocol0.shared.Config import Config


class InstrumentSimpler(InstrumentInterface):
    NAME = "Simpler"
    TRACK_COLOR = InstrumentColorEnum.SIMPLER
    PRESETS_PATH = Config.SAMPLE_DIRECTORY
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.CATEGORY
    CAN_BE_SHOWN = False
    PRESET_CHANGER = SamplePresetChanger

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.device = cast(SimplerDevice, self.device)
