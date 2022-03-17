from functools import partial

from typing import TYPE_CHECKING, Optional, Type

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.InstrumentPresetList import InstrumentPresetList
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import PresetChangerInterface
from protocol0.domain.lom.instrument.preset.preset_changer.ProgramChangePresetChanger import ProgramChangePresetChanger
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImporterFactory import PresetImporterFactory
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerDevicePresetName import \
    PresetInitializerDevicePresetName
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerInterface import \
    PresetInitializerInterface
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class InstrumentInterface(object):
    NAME = ""
    DEVICE_NAME = ""
    TRACK_COLOR = InstrumentColorEnum.UNKNOWN
    CAN_BE_SHOWN = True
    PRESETS_PATH = ""
    PRESET_EXTENSION = ""
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NAME
    HAS_PROTECTED_MODE = True
    PRESET_OFFSET = 0  # if we store presets not at the beginning of the list
    MIDI_INPUT_ROUTING_TYPE = InputRoutingTypeEnum.ALL_INS
    PRESET_CHANGER = ProgramChangePresetChanger  # type: Type[PresetChangerInterface]
    PRESET_INITIALIZER = PresetInitializerDevicePresetName  # type: Type[PresetInitializerInterface]

    def __init__(self, track, device):
        # type: (SimpleTrack, Optional[Device]) -> None
        self.track = track  # this could be a group track
        self.device = device
        self.activated = False
        preset_importer = PresetImporterFactory.create_importer(device, self.PRESETS_PATH, self.PRESET_EXTENSION)
        preset_initializer = self.PRESET_INITIALIZER(device, track)
        preset_changer = self.PRESET_CHANGER(device, self.PRESET_OFFSET)

        self.preset_list = InstrumentPresetList(preset_importer, preset_initializer, preset_changer)

    def __repr__(self):
        # type: () -> str
        return self.__class__.__name__

    @property
    def name(self):
        # type: () -> str
        if self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME and self.selected_preset:
            return self.selected_preset.name
        elif self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY and \
                self.preset_list.selected_category:
            return self.preset_list.selected_category
        elif self.NAME:
            return self.NAME
        else:
            return self.device.name

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        return False

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        pass

    def post_activate(self):
        # type: () -> Optional[Sequence]
        pass

    @property
    def selected_preset(self):
        # type: () -> Optional[InstrumentPreset]
        return self.preset_list.selected_preset

    def scroll_presets(self, go_next):
        # type: (bool) -> Sequence
        seq = Sequence()
        seq.add(self.track.abstract_track.arm)
        seq.add(partial(self.preset_list.scroll, go_next))
        seq.add(self.track.abstract_track.refresh_appearance)
        return seq.done()
