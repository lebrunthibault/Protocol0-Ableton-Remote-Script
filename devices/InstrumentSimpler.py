import os

from typing import List, Any, Optional

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.devices.presets.InstrumentPreset import InstrumentPreset
from protocol0.enums.ColorEnum import ColorEnum
from protocol0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.lom.Note import Note
from protocol0.lom.clip.MidiClip import MidiClip
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

    def _load_preset(self, preset):
        # type: (InstrumentPreset) -> Optional[Sequence]
        self.parent.browserManager.load_sample(preset.original_name)  # type: ignore[arg-type]
        self.parent.wait(400, self.track._devices_listener)
        return None

    def generate_base_notes(self, clip):
        # type: (MidiClip) -> List[Note]
        """ overridden """
        # add c3 note
        return [Note(pitch=60, velocity=127, start=0, duration=min(1, int(clip.length)), clip=clip)]
