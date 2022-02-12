import os

from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.SampleSelectedEvent import SampleSelectedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class InstrumentSimpler(InstrumentInterface):
    NAME = "Simpler"
    TRACK_COLOR = InstrumentColorEnum.SIMPLER
    PRESET_EXTENSION = ".wav"
    PRESETS_PATH = str(os.getenv("SAMPLE_PATH"))
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.CATEGORY
    CAN_BE_SHOWN = False

    def __init__(self, track, device):
        # type: (SimpleTrack, Optional[Device]) -> None
        super(InstrumentSimpler, self).__init__(track, device)
        self.device = self.device  # type: SimplerDevice

    def load_preset(self, preset):
        # type: (InstrumentPreset) -> None
        DomainEventBus.notify(SampleSelectedEvent(str(preset.original_name)))
