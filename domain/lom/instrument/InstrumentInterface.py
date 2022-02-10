from typing import TYPE_CHECKING, Optional

from _Framework.Util import forward_property
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.InstrumentPresetList import InstrumentPresetList
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import PresetProgramSelectedEvent
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.domain.shared.DomainEventBus import DomainEventBus

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
    PROGRAM_CHANGE_OFFSET = 0  # if we store presets not at the beginning of the list
    MONOPHONIC = False

    def __init__(self, track, device):
        # type: (SimpleTrack, Optional[Device]) -> None
        self.track = track  # this could be a group track
        self.device = device
        self.activated = False
        self.preset_list = InstrumentPresetList(self.device, self.PRESETS_PATH, self.PRESET_EXTENSION, self.PRESET_DISPLAY_OPTION, self.track.abstract_track.name)

    @property
    def name(self):
        # type: () -> str
        if self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY and \
                self.preset_list and \
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
    def can_change_presets(self):
        # type: () -> bool
        return True

    # noinspection PyMethodParameters
    @forward_property("preset_list")
    def selected_preset():
        # type: () -> Optional[InstrumentPreset]
        pass

    def load_preset(self, preset):
        # type: (InstrumentPreset) -> None
        """ Overridden default is send program change """
        DomainEventBus.notify(PresetProgramSelectedEvent(preset.index + self.PROGRAM_CHANGE_OFFSET))
