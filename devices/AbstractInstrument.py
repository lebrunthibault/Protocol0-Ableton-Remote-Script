from functools import partial

from typing import TYPE_CHECKING, List, Optional

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.devices.presets.InstrumentPreset import InstrumentPreset
from a_protocol_0.devices.presets.InstrumentPresetList import InstrumentPresetList
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractInstrument(AbstractObject):
    __subject_events__ = ('selected_preset',)

    INSTRUMENT_NAME_MAPPINGS = {
        "serum_x64": "InstrumentSerum",
        "minitaur editor-vi(x64)": "InstrumentMinitaur",
        "rev2editor": "InstrumentProphet",
    }

    NAME = "AbstractInstrument"
    TRACK_COLOR = Colors.DISABLED
    NUMBER_OF_PRESETS = 128
    PRESETS_PATH = None
    PRESET_EXTENSION = ""
    NEEDS_EXCLUSIVE_ACTIVATION = False
    NEEDS_ACTIVATION_FOR_PRESETS_CHANGE = False
    IS_EXTERNAL_SYNTH = False
    SHOULD_DISPLAY_SELECTED_PRESET_NAME = True
    SHOULD_DISPLAY_SELECTED_PRESET_INDEX = True
    SHOULD_UPDATE_TRACK_NAME = True

    _active_instance = None  # type: AbstractInstrument

    def __init__(self, track, device, *a, **k):
        # type: (SimpleTrack, Device) -> None
        super(AbstractInstrument, self).__init__(*a, **k)
        self.track = track  # this could be a group track
        self.device_track = track  # this will always be the track of the device
        self.device = device  # type: Device
        if device:
            self.can_be_shown = True
            self.activated = False
            self.name = device.name
        else:
            self.can_be_shown = False
            self.activated = True
            self.name = self.__class__.__name__

        self.preset_list = InstrumentPresetList(self)  # type: InstrumentPresetList
        self._selected_preset_index = self.track.selected_preset_index
        self._base_name_listener.subject = track.track_name

    @property
    def selected_preset(self):
        # type: () -> InstrumentPreset
        return self.preset_list.selected_preset

    @property
    def should_display_selected_preset_name(self):
        return self.preset_list.has_preset_names and self.SHOULD_DISPLAY_SELECTED_PRESET_NAME

    @property
    def active_instance(self):
        return self.__class__._active_instance

    @active_instance.setter
    def active_instance(self, instance):
        self.__class__._active_instance = instance

    @subject_slot("base_name")
    def _base_name_listener(self):
        self.parent.log_dev("base name listener !!!!")
        self.preset_list.import_presets()
        self.parent.log_dev(self.selected_preset)
        self.sync_selected_preset()

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        return

    @property
    def should_be_activated(self):
        if not self.can_be_shown:
            return False
        return not self.activated or (self.NEEDS_EXCLUSIVE_ACTIVATION and self.active_instance != self)

    def check_activated(self):
        if not self.should_be_activated:
            return

        seq = Sequence()

        if not self.activated:
            seq.add(self.device.track.select)
            seq.add(partial(self.parent.deviceManager.check_plugin_window_showable, self.device))
            seq.add(lambda: setattr(self, "activated", True), name="mark instrument as activated")

        if self.NEEDS_EXCLUSIVE_ACTIVATION and self.active_instance != self:
            seq.add(self.exclusive_activate)
            seq.add(partial(setattr, self, "active_instance", self))

        seq.add(self.song.selected_track.select, silent=True)

        return seq.done()

    def show_hide(self):
        is_shown = self.parent.keyboardShortcutManager.is_plugin_window_visible(self.name)
        if not self.should_be_activated or is_shown:
            seq = Sequence()
            seq.add(self.device.track.select)
            # happens when clicking from current track
            seq.add(self.parent.keyboardShortcutManager.show_hide_plugins, do_if_not=lambda: self.parent.keyboardShortcutManager.is_plugin_window_visible(self.name) and not is_shown)
            seq.done()
        else:
            self.check_activated()

    @property
    def presets_path(self):
        """ overridden """
        return self.PRESETS_PATH

    def format_preset_name(self, preset_name):
        # type: (str) -> str
        """ overridden """
        return preset_name

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        seq = Sequence()
        if self.device:
            seq.add(self.device_track.select)
            if self.NEEDS_ACTIVATION_FOR_PRESETS_CHANGE:
                seq.add(self.check_activated)

        seq.add(partial(self.preset_list.scroll, go_next=go_next))
        seq.add(partial(self.sync_selected_preset))
        return seq.done()

    def sync_selected_preset(self):
        self.parent.log_dev(self.selected_preset)
        seq = Sequence()
        seq.add(partial(self.load_preset, self.selected_preset))
        seq.add(partial(self.parent.show_message, "preset change : %s" % self.selected_preset.name or self.selected_preset.index))
        # noinspection PyUnresolvedReferences
        seq.add(self.notify_selected_preset)
        return seq.done()

    def load_preset(self, preset):
        # type: (InstrumentPreset) -> Sequence
        """ Overridden default is send program change """
        seq = Sequence()
        seq.add(self.track.action_arm)
        seq.add(self.parent.midiManager.send_program_change(preset.index))
        return seq.done()

    def action_scroll_categories(self, go_next):
        # type: (bool) -> None
        self.parent.log_error("this instrument does not have scrollable categories")
