import os
from os.path import isfile, isdir
from typing import TYPE_CHECKING, Any, List

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class AbstractInstrument(AbstractObject):
    NUMBER_OF_PRESETS = 128
    PRESETS_PATH = None

    def __init__(self, track, device, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractInstrument, self).__init__(*a, **k)
        self.track = track
        self._device = device
        self.name = device.name
        self.activated = False
        self.can_be_shown = True
        self.has_rack = track.all_devices.index(device) != 0
        self.preset_names = []  # type: List[str]
        self.get_presets()

    def check_activated(self):
        if self.can_be_shown and not self.activated:
            self.song.select_track(self.track)
            self.activate()
            self.activated = True

    def get_presets(self):
        if self.PRESETS_PATH:
            if isfile(self.PRESETS_PATH):
                self.preset_names = open(self.PRESETS_PATH).readlines()
            elif isdir(self.PRESETS_PATH):
                self.preset_names = os.listdir(self.PRESETS_PATH)

        self.NUMBER_OF_PRESETS = len(self.preset_names) or self.NUMBER_OF_PRESETS

    def get_display_name(self, preset_name):
        # type: (str) -> str
        return preset_name

    def activate(self):
        # type: () -> None
        """ for instruments needing gui click activation """
        if self.has_rack:
            self.parent.ahkManager.toggle_first_vst_with_rack()
        else:
            self.parent.ahkManager.toggle_first_vst()

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        if TrackName(self.track).preset_index == -1:
            new_preset_index = 0
        else:
            new_preset_index = TrackName(self.track).preset_index + 1 if go_next else TrackName(self.track).preset_index - 1
        new_preset_index %= self.NUMBER_OF_PRESETS

        TrackName(self.track).set(preset_index=new_preset_index)

        display_preset = self.preset_names[new_preset_index] if len(self.preset_names) else str(new_preset_index)
        display_preset = os.path.splitext(self.get_display_name(display_preset))[0]
        self.parent.show_message("preset change : %s" % self.get_display_name(display_preset))
        self.set_preset(new_preset_index, go_next)

    def set_preset(self, preset_index, _):
        # type: (int, bool) -> None
        """ default is send program change """
        self.parent.midiManager.send_program_change(preset_index)
