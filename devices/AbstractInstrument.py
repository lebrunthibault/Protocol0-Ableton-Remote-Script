import os
import re
from functools import partial
from os import listdir

from typing import TYPE_CHECKING, Optional, List, Any, Type

from a_protocol_0.devices.AbstractInstrumentPresetsMixin import AbstractInstrumentPresetsMixin
from a_protocol_0.enums.ColorEnum import ColorEnum
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.PluginDevice import PluginDevice
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.lom.device.SimplerDevice import SimplerDevice
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractInstrument(AbstractInstrumentPresetsMixin, AbstractObject):
    __subject_events__ = ("selected_preset",)

    # computed at boot time
    INSTRUMENT_CLASSES = []  # type: List[Type[AbstractInstrument]]

    NAME = ""
    DEVICE_NAME = ""
    TRACK_COLOR = ColorEnum.DISABLED
    CAN_BE_SHOWN = True
    IS_EXTERNAL_SYNTH = False

    _active_instance = None  # type: AbstractInstrument

    def __init__(self, track, device, *a, **k):
        # type: (SimpleTrack, Optional[Device], Any, Any) -> None
        super(AbstractInstrument, self).__init__(*a, **k)
        self.track = track  # this could be a group track
        self.device = device
        self.activated = False
        self._import_presets()

    @property
    def name(self):
        # type: () -> str
        if self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            return self._preset_list.selected_category or "None"
        elif self.NAME:
            return self.NAME
        else:
            return self.device.name

    @classmethod
    def get_instrument_classes(cls):
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

    @classmethod
    def _get_device_from_rack_device(cls, rack_device):
        # type: (RackDevice) -> Optional[Device]
        if len(rack_device.chains) and len(rack_device.chains[0].devices):
            # keeping only racks containing the same device
            device_types = list(set([type(chain.devices[0]) for chain in rack_device.chains if len(chain.devices)]))
            device_names = list(set([chain.devices[0].name for chain in rack_device.chains if len(chain.devices)]))
            if len(device_types) == 1 and len(device_names) == 1:
                return rack_device.chains[0].devices[0]

        return None

    @classmethod
    def get_instrument_class(cls, device):
        # type: (Device) -> Optional[Type[AbstractInstrument]]
        # checking for grouped devices
        if isinstance(device, RackDevice):
            device = cls._get_device_from_rack_device(device) or device

        if isinstance(device, PluginDevice):
            for _class in cls.INSTRUMENT_CLASSES:
                if _class.DEVICE_NAME.lower() == device.name.lower():
                    return _class
        elif isinstance(device, SimplerDevice):
            from a_protocol_0.devices.InstrumentSimpler import InstrumentSimpler

            return InstrumentSimpler
        elif device.can_have_drum_pads:
            from a_protocol_0.devices.InstrumentDrumRack import InstrumentDrumRack

            return InstrumentDrumRack

        return None

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        """ overridden """
        return False

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        pass

    def check_activated(self, select_instrument_track=False):
        # type: (bool) -> Optional[Sequence]
        if not self.CAN_BE_SHOWN or (self.activated and not self.needs_exclusive_activation):
            return None

        seq = Sequence()

        if not self.activated:
            seq.add(self.device.track.select)
            seq.add(partial(self.parent.deviceManager.make_plugin_window_showable, self.device))
            seq.add(lambda: setattr(self, "activated", True), name="mark instrument as activated")

        if self.needs_exclusive_activation:
            seq.add(self.device.track.select)
            seq.add(self.exclusive_activate)

        if not select_instrument_track:
            seq.add(self.song.selected_track.select, silent=True)

        return seq.done()

    def show_hide(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(partial(self.check_activated, select_instrument_track=True))
        seq.add(self.device.track.select)
        if self.song.selected_track != self.device.track or not self.is_plugin_window_visible:
            seq.add(self.parent.keyboardShortcutManager.show_plugins)
        else:
            seq.add(self.parent.keyboardShortcutManager.show_hide_plugins)
        return seq.done()

    @property
    def is_plugin_window_visible(self):
        # type: () -> bool
        return self.parent.keyboardShortcutManager.is_plugin_window_visible(self.device.name)

    def generate_base_notes(self, clip):
        # type: (Clip) -> List[Note]
        """ overridden """
        return []
