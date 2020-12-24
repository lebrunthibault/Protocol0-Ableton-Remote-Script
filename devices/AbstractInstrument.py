import os
from os import listdir
from os.path import isfile, isdir, join
from typing import TYPE_CHECKING, List

import Live

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class AbstractInstrument(AbstractObject):
    NUMBER_OF_PRESETS = 128
    PRESETS_PATH = None
    PRESET_EXTENSION = ""

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
        self.parent.defer(self.get_presets)
        self._base_name_listener.subject = track

    @subject_slot("base_name")
    def _base_name_listener(self):
        self.parent.log_debug("base_name changed !!! -> %s" % self.name)
        self.get_presets(set_preset=True)

    def check_activated(self):
        if self.can_be_shown and not self.activated:
            self.song.select_track(self.device_track)
            self._activate()
            self.activated = True

    def show(self):
        if not self.can_be_shown:
            return
        if not self.activated:
            self._activate()
            self.activated = True
        else:
            self.parent.keyboardShortcutManager.show_hide_plugins()

    def _activate(self):
        # type: () -> None
        self.parent.deviceManager.show_device(device=self._device, track=self.device_track)

    def _get_presets_path(self):
        return self.PRESETS_PATH

    def get_presets(self, set_preset=False):
        presets_path = self._get_presets_path()
        if presets_path:
            if isfile(presets_path):
                self.preset_names = open(presets_path).readlines()
            elif isdir(presets_path):
                self.preset_names = [f for f in listdir(presets_path) if isfile(join(presets_path, f)) and f.endswith(self.PRESET_EXTENSION)]

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
        self.check_activated()
        self._scroll_presets_or_sample(go_next)

    def _scroll_presets_or_sample(self, go_next):
        # type: (bool) -> None
        new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index %= self.NUMBER_OF_PRESETS

        TrackName(self.track).set(preset_index=new_preset_index)

        display_preset = self.preset_names[new_preset_index] if len(self.preset_names) else str(new_preset_index)
        display_preset = os.path.splitext(self.get_display_name(display_preset))[0]
        self.parent.show_message("preset change : %s" % self.get_display_name(display_preset))
        self.set_preset(new_preset_index)

    def set_preset(self, preset_index):
        # type: (int) -> None
        """ default is send program change """
        self.track.action_arm()
        self.parent.midiManager.send_program_change(preset_index)
