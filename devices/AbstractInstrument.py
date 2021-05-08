import os
import re
from functools import partial
from os import listdir

from typing import TYPE_CHECKING, Optional, List, Any, Type

from a_protocol_0.devices.presets.InstrumentPreset import InstrumentPreset
from a_protocol_0.devices.presets.InstrumentPresetList import InstrumentPresetList
from a_protocol_0.enums.ColorEnum import ColorEnum
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.PluginDevice import PluginDevice
from a_protocol_0.lom.device.SimplerDevice import SimplerDevice
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractInstrument(AbstractObject):
    __subject_events__ = ("selected_preset",)

    # computed at boot time
    INSTRUMENT_CLASSES = []  # type: List[Type[AbstractInstrument]]

    NAME = ""
    DEVICE_NAME = ""
    TRACK_COLOR = ColorEnum.DISABLED
    CAN_BE_SHOWN = True
    NUMBER_OF_PRESETS = 128
    PRESETS_PATH = ""
    PRESET_EXTENSION = ""
    NEEDS_ACTIVATION_FOR_PRESETS_CHANGE = False
    IS_EXTERNAL_SYNTH = False
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NAME
    PROGRAM_CHANGE_OFFSET = 0  # if we store presets not at the beginning of the list

    _active_instance = None  # type: AbstractInstrument

    def __init__(self, track, device, *a, **k):
        # type: (SimpleTrack, Optional[Device], Any, Any) -> None
        super(AbstractInstrument, self).__init__(*a, **k)
        self.track = track  # this could be a group track
        self.device = device
        self.activated = False
        self._preset_list = InstrumentPresetList(self)  # type: InstrumentPresetList

    @property
    def name(self):
        # type: () -> str
        return self.NAME if self.NAME else self.device.name

    @staticmethod
    def get_instrument_classes():
        # type: () -> List[Type[AbstractInstrument]]
        files = listdir(os.path.dirname(os.path.abspath(__file__)))

        class_names = []
        for file in [file for file in files if re.match("^Instrument[a-zA-Z]*\.py$", file)]:
            class_name = file.replace(".py", "")
            try:
                mod = __import__("a_protocol_0.devices." + class_name, fromlist=[class_name])
            except ImportError:
                raise Protocol0Error("Import Error on class %s" % class_name)

            class_names.append(getattr(mod, class_name))

        return class_names

    @staticmethod
    def get_instrument_class(device):
        # type: (Device) -> Optional[Type[AbstractInstrument]]
        if isinstance(device, PluginDevice):
            for _class in AbstractInstrument.INSTRUMENT_CLASSES:
                if _class.DEVICE_NAME.lower() == device.name.lower():
                    return _class
        elif isinstance(device, SimplerDevice):
            from a_protocol_0.devices.InstrumentSimpler import InstrumentSimpler

            return InstrumentSimpler
        elif device.can_have_drum_pads:
            from a_protocol_0.devices.InstrumentDrumRack import InstrumentDrumRack

            return InstrumentDrumRack

        return None

    def sync_presets(self):
        # type: () -> None
        self._preset_list.sync_presets()

    @property
    def selected_preset(self):
        # type: () -> Optional[InstrumentPreset]
        return self._preset_list.selected_preset

    @property
    def should_display_selected_preset_name(self):
        # type: () -> bool
        return self._preset_list.has_preset_names and self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME

    @property
    def active_instance(self):
        # type: () -> Optional[AbstractInstrument]
        return self.__class__._active_instance

    @active_instance.setter
    def active_instance(self, instance):
        # type: (AbstractInstrument) -> None
        self.__class__._active_instance = instance

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        return False

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        pass

    @property
    def should_be_activated(self):
        # type: () -> bool
        if not self.CAN_BE_SHOWN:
            return False
        return not self.activated or (self.needs_exclusive_activation)

    def check_activated(self, select_instrument_track=False):
        # type: (bool) -> Optional[Sequence]
        if not self.should_be_activated:
            return None

        seq = Sequence()

        if not self.activated:
            seq.add(self.device.track.select)
            seq.add(partial(self.parent.deviceManager.make_plugin_window_showable, self.device))
            seq.add(lambda: setattr(self, "activated", True), name="mark instrument as activated")

        if self.needs_exclusive_activation:
            seq.add(self.exclusive_activate)

        if not select_instrument_track:
            seq.add(self.song.selected_track.select, silent=True)

        return seq.done()

    def show_hide(self):
        # type: () -> None
        is_shown = self.parent.keyboardShortcutManager.is_plugin_window_visible(self.name)
        if not self.should_be_activated or is_shown:
            seq = Sequence()
            seq.add(self.device.track.select)
            # happens when clicking from current track
            seq.add(
                self.parent.keyboardShortcutManager.show_hide_plugins,
                do_if_not=lambda: self.parent.keyboardShortcutManager.is_plugin_window_visible(self.name)
                and not is_shown,
            )
            seq.done()
        else:
            self.check_activated(select_instrument_track=True)

    @property
    def presets_path(self):
        # type: () -> str
        """ overridden """
        return self.PRESETS_PATH

    def format_preset_name(self, preset_name):
        # type: (str) -> str
        """ overridden """
        return preset_name

    @property
    def preset_name(self):
        # type: () -> str
        """ overridden """
        return self.name

    def scroll_presets_or_samples(self, go_next):
        # type: (bool) -> Sequence
        self.parent.clyphxNavigationManager.show_track_view()

        seq = Sequence()
        if self.NEEDS_ACTIVATION_FOR_PRESETS_CHANGE:
            seq.add(self.check_activated)

        seq.add(partial(self._preset_list.scroll, go_next=go_next))
        seq.add(partial(self._sync_selected_preset))
        return seq.done()

    def scroll_preset_categories(self, go_next):
        # type: (bool) -> None
        self.parent.log_error("this instrument does not have scrollable categories")

    def _sync_selected_preset(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(partial(self._load_preset, self.selected_preset))
        seq.add(partial(self.parent.show_message, "preset change : %s" % self.selected_preset))
        # noinspection PyUnresolvedReferences
        seq.add(self.notify_selected_preset)
        return seq.done()

    def _load_preset(self, preset):
        # type: (InstrumentPreset) -> Optional[Sequence]
        """ Overridden default is send program change """
        seq = Sequence()
        seq.add(self.track.abstract_track.arm)
        seq.add(partial(self.parent.midiManager.send_program_change, preset.index + self.PROGRAM_CHANGE_OFFSET))
        return seq.done()

    def generate_base_notes(self, clip):
        # type: (Clip) -> List[Note]
        """ overridden """
        return []
