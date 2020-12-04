import os
from os.path import isfile, isdir
from typing import TYPE_CHECKING, Any, List

from a_protocol_0.devices.Device import Device
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class AbstractInstrument(Device):
    NUMBER_OF_PRESETS = 128
    PRESETS_PATH = None

    def __init__(self, track, has_rack, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractInstrument, self).__init__(*a, **k)
        self.track = track
        self.needs_activation = False
        self.can_be_shown = True
        self.has_rack = has_rack
        self.preset_names = []  # type: List[str]
        self.get_presets()
        self.parent.log(self.name)
        self.parent.log(self.has_rack)

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
        pass

    def show(self):
        # type: () -> None
        if self.has_rack:
            self.parent.ahkManager.toggle_first_vst_with_rack()
        else:
            self.parent.ahkManager.toggle_first_vst()

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        if TrackName(self).preset_index == -1:
            new_preset_index = 0
        else:
            new_preset_index = TrackName(self).preset_index + 1 if go_next else TrackName(self).preset_index - 1
        new_preset_index %= self.NUMBER_OF_PRESETS

        self.track.name = TrackName(self.track).get_track_name_for_preset_index(new_preset_index)

        display_preset = self.preset_names[new_preset_index] if len(self.preset_names) else str(new_preset_index)
        self.parent.show_message("preset change : %s" % display_preset)
        self.set_preset(new_preset_index, go_next)

    def set_preset(self, preset_index, _):
        # type: (int, bool) -> None
        """ default is send program change """
        self.parent.midiManager.send_program_change(preset_index)
