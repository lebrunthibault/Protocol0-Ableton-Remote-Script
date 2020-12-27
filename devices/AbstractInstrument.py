import os
from os.path import isfile, isdir
from typing import TYPE_CHECKING, List

import Live

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.Sequence import Sequence
from a_protocol_0.utils.decorators import debounce
from a_protocol_0.utils.log import log_ableton

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractInstrument(AbstractObject):
    NUMBER_OF_PRESETS = 128
    PRESETS_PATH = None
    PRESET_EXTENSION = ""
    NEEDS_EXCLUSIVE_ACTIVATION = False
    _active_instance = None  # type: AbstractInstrument

    def __init__(self, track, device, *a, **k):
        # type: (SimpleTrack, Live.Device.Device) -> None
        super(AbstractInstrument, self).__init__(*a, **k)
        self.track = track
        self.device_track = track
        self._device = device
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
        self._base_name_listener.subject = track

    @property
    def active_instance(self):
        return self.__class__._active_instance

    @active_instance.setter
    def active_instance(self, instance):
        self.__class__._active_instance = instance

    @subject_slot("base_name")
    def _base_name_listener(self):
        TrackName(self.track).preset_index = 0
        self.get_presets(set_preset=True)

    def exclusive_activate(self):
        # type: () -> Sequence
        pass

    def check_activated(self, auto_hide=True):
        # type: (bool) -> None
        if not self.can_be_shown:
            return

        on_finish_seq = Sequence(name="on_finish")

        self.parent.log_debug((self.active_instance, self, self.NEEDS_EXCLUSIVE_ACTIVATION and self.active_instance != self))
        if self.NEEDS_EXCLUSIVE_ACTIVATION and self.active_instance != self:
            on_finish_seq.add(self.exclusive_activate())

        seq = Sequence([], interval=0, on_finish=on_finish_seq, name="click sequence")
        if not self.activated:
            self.song.select_track(self.device_track)
            on_finish_seq.add(lambda: setattr(self, "activated", True), interval=0)
            self.parent.deviceManager.check_plugin_window_showable(self._device, self.device_track, seq=seq, auto_hide=auto_hide)
        elif not auto_hide:
            on_finish_seq.add(self.parent.keyboardShortcutManager.show_hide_plugins)
        else:
            on_finish_seq.add(lambda: self.song.select_track(self.track), interval=1)

        seq()

    def show_hide(self):
        self.check_activated(auto_hide=False)

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
        if self._device:
            self.song.select_device(self._device)
            self._device.view.is_collapsed = False
        self._scroll_presets_or_sample(go_next)

    def _scroll_presets_or_sample(self, go_next):
        # type: (bool) -> None
        new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index %= self.NUMBER_OF_PRESETS

        TrackName(self.track).preset_index = new_preset_index

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
