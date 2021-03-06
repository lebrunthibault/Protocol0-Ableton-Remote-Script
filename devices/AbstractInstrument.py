import os
from functools import partial
from os.path import isfile, isdir

from typing import TYPE_CHECKING, List, Optional

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import debounce

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractInstrument(AbstractObject):
    NUMBER_OF_PRESETS = 128
    PRESETS_PATH = None
    PRESET_EXTENSION = ""
    NEEDS_EXCLUSIVE_ACTIVATION = False
    NEEDS_ACTIVATION_FOR_PRESETS_CHANGE = False
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
        self.preset_names = []  # type: List[str]
        self.get_presets()
        self._base_name_listener.subject = track.track_name

    @property
    def active_instance(self):
        return self.__class__._active_instance

    @active_instance.setter
    def active_instance(self, instance):
        self.__class__._active_instance = instance

    @subject_slot("base_name")
    def _base_name_listener(self):
        self.get_presets(set_preset=True)

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        return

    @property
    def should_be_activated(self):
        return not self.activated or (self.NEEDS_EXCLUSIVE_ACTIVATION and self.active_instance != self)

    def check_activated(self, keep_focus=False):
        if not self.can_be_shown:
            return

        seq = Sequence()

        if not self.activated:
            seq.add(partial(self.song.select_track, self.device.track))
            seq.add(partial(self.parent.deviceManager.check_plugin_window_showable, self.device))
            seq.add(lambda: setattr(self, "activated", True), name="mark instrument as activated")

        if self.NEEDS_EXCLUSIVE_ACTIVATION and self.active_instance != self:
            seq.add(self.exclusive_activate)
            seq.add(partial(setattr, self, "active_instance", self))

        if not keep_focus:
            seq.add(partial(self.song.select_track, self.song.selected_track))

        return seq.done()

    def show_hide(self):
        is_shown = self.parent.keyboardShortcutManager.is_plugin_window_visible(self.name)
        if not self.should_be_activated or is_shown:
            seq = Sequence()
            seq.add(partial(self.song.select_track, self.device.track))
            # happens when clicking from current track
            seq.add(self.parent.keyboardShortcutManager.show_hide_plugins, do_if_not=lambda: self.parent.keyboardShortcutManager.is_plugin_window_visible(self.name) and not is_shown)
            seq.done()
        else:
            self.check_activated()

    def _get_presets_path(self):
        return self.PRESETS_PATH

    @debounce()
    def get_presets(self, set_preset=False):
        self.preset_names = []  # type: List[str]
        presets_path = self._get_presets_path()
        if not presets_path:
            return

        if isfile(presets_path):
            self.preset_names = open(presets_path).readlines()
        elif isdir(presets_path):
            for root, sub_dirs, files in os.walk(presets_path):
                for file in files:
                    if file.endswith(self.PRESET_EXTENSION):
                        self.preset_names.append(file)

        self.NUMBER_OF_PRESETS = len(self.preset_names) or self.NUMBER_OF_PRESETS
        if set_preset:
            self.set_preset(self.track.preset_index)

    def get_display_name(self, preset_name):
        # type: (str) -> str
        return preset_name

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        seq = Sequence()
        if self.device:
            seq.add(partial(self.song.select_track, self.device_track))
            # note: in the case of fast scrolling on a simpler, _devices_listener is not called in time
            # so the following could fail but will succeed just after so we just ignore the error
            seq.add(partial(self.song.select_device, self.device), silent=True)
            if self.NEEDS_ACTIVATION_FOR_PRESETS_CHANGE:
                seq.add(self.check_activated)
            seq.add(lambda: setattr(self.device, "is_collapsed", False))

        seq.add(partial(self._scroll_presets_or_sample, go_next))
        return seq.done()

    def _scroll_presets_or_sample(self, go_next):
        # type: (bool) -> None
        new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index %= self.NUMBER_OF_PRESETS

        self.track.track_name.set(preset_index=new_preset_index)

        display_preset = self.preset_names[new_preset_index] if len(self.preset_names) else str(new_preset_index)
        display_preset = os.path.splitext(self.get_display_name(display_preset))[0]
        self.parent.show_message("preset change : %s" % self.get_display_name(display_preset))
        self.set_preset(new_preset_index)

    def set_preset(self, preset_index):
        # type: (int) -> None
        """ default is send program change """
        self.track.action_arm()
        self.parent.midiManager.send_program_change(preset_index)

    def action_scroll_categories(self, go_next):
        # type: (bool) -> None
        self.parent.log_error("this instrument does not have scrollable categories")
