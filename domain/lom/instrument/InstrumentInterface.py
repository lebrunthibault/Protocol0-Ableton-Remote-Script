from functools import partial

from _Framework.SubjectSlot import SlotManager
from typing import Optional, Type, TYPE_CHECKING

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.InstrumentPresetList import InstrumentPresetList
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.lom.instrument.preset.preset_changer.ProgramChangePresetChanger import (
    ProgramChangePresetChanger,
)
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImporterFactory import (
    PresetImporterFactory,
)
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerDevicePresetName import (
    PresetInitializerDevicePresetName,
)
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerInterface import (
    PresetInitializerInterface,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


def _get_insert_instrument_track(instrument_cls):
    # type: (Type["InstrumentInterface"]) -> SimpleTrack
    """Current track or last instrument track or last track"""
    target_color = instrument_cls.TRACK_COLOR.value

    if Song.current_track().color == target_color:
        return Song.current_track().base_track

    instrument_tracks = [
        t
        for t in Song.simple_tracks()
        if t.group_track is None and t.color == target_color
    ]

    last_track = list(Song.top_tracks())[-1].base_track

    return next(reversed(instrument_tracks), last_track)


def load_instrument_track(instrument_cls):
    # type: (Type["InstrumentInterface"]) -> Sequence
    insert_track = _get_insert_instrument_track(instrument_cls)
    track_color = insert_track.color


    seq = Sequence()
    seq.add(insert_track.focus)
    seq.add(partial(Backend.client().load_instrument_track, instrument_cls.INSTRUMENT_TRACK_NAME))
    seq.wait_for_backend_event("instrument_loaded")
    seq.add(partial(setattr, insert_track, "color", track_color))
    return seq.done()


class InstrumentInterface(SlotManager):
    NAME = ""
    DEVICE = None  # type: Optional[DeviceEnum]
    TRACK_COLOR = InstrumentColorEnum.UNKNOWN
    CAN_BE_SHOWN = True
    PRESETS_PATH = ""
    PRESET_EXTENSION = ""
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NAME
    DEFAULT_NOTE = 60
    PRESET_OFFSET = 0  # if we store presets not at the beginning of the list
    PRESET_CHANGER = ProgramChangePresetChanger  # type: Type[PresetChangerInterface]
    PRESET_INITIALIZER = PresetInitializerDevicePresetName  # type: Type[PresetInitializerInterface]
    INSTRUMENT_TRACK_NAME = ""
    IS_EXTERNAL_SYNTH = False

    def __init__(self, device, track_name):
        # type: (Optional[Device], str) -> None
        super(InstrumentInterface, self).__init__()
        self._track_name = track_name
        self.device = device

        preset_importer = PresetImporterFactory.create_importer(
            device, self.PRESETS_PATH, self.PRESET_EXTENSION
        )
        preset_initializer = self.PRESET_INITIALIZER(device, track_name)
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
        elif (
            self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY
            and self.preset_list.selected_category
        ):
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

    def set_default_preset(self):
        # type: () -> None
        raise Protocol0Warning("No default preset for %s" % self)
