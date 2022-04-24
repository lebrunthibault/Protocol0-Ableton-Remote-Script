from typing import Optional, TYPE_CHECKING, cast

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.preset_changer.SamplePresetChanger import SamplePresetChanger
from protocol0.shared.Config import Config

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class InstrumentSimpler(UseFrameworkEvents, InstrumentInterface):
    NAME = "Simpler"
    TRACK_COLOR = InstrumentColorEnum.SIMPLER
    PRESET_EXTENSION = ".wav"
    PRESETS_PATH = Config.SAMPLE_DIRECTORY
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.CATEGORY
    CAN_BE_SHOWN = False
    PRESET_CHANGER = SamplePresetChanger

    def __init__(self, track, device):
        # type: (SimpleTrack, Optional[SimplerDevice]) -> None
        super(InstrumentSimpler, self).__init__(track, device)
        self.device = cast(SimplerDevice, self.device)
