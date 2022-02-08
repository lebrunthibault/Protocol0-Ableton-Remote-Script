import os

from typing import Optional, TYPE_CHECKING

import Live
from protocol0.domain.command.LoadSampleCommand import LoadSampleCommand
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.shared.CommandBus import CommandBus
from protocol0.shared.SongFacade import SongFacade

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
        SongFacade.selected_track.device_insert_mode = Live.Track.DeviceInsertMode.default
        CommandBus.dispatch(LoadSampleCommand(preset.original_name))  # type: ignore[arg-type]
