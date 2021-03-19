import os
from os import listdir
from os.path import join

from _Framework.Util import find_if
from typing import Optional

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.devices.presets.InstrumentPreset import InstrumentPreset
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.utils.utils import scroll_values


class InstrumentSimpler(AbstractInstrument):
    NAME = "Simpler"
    TRACK_COLOR = Colors.SIMPLER
    PRESET_EXTENSION = ".wav"
    PRESETS_PATH = os.getenv("SAMPLE_PATH")
    SHOULD_DISPLAY_SELECTED_PRESET_NAME = False
    SHOULD_DISPLAY_SELECTED_PRESET_INDEX = False
    SHOULD_UPDATE_TRACK_NAME = False

    def __init__(self, *a, **k):
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.can_be_shown = False
        self.activated = True

    @property
    def selected_category(self):
        # type: () -> Optional[str]
        """ the name of the track is the name of a sample sub_directory """
        selected_category = find_if(lambda f: self.track.base_name.lower() in f.lower(), listdir(self.PRESETS_PATH))
        if not selected_category:
            raise Protocol0Error("Couldn't find sample selected category for %s" % self.track)

        return selected_category

    @property
    def presets_path(self):
        # type: () -> str
        return join(self.PRESETS_PATH, self.selected_category)

    def load_preset(self, preset):
        # type: (InstrumentPreset) -> None
        self.parent.browserManager.load_sample(preset.original_name)
        self.parent._wait(4, self.track._devices_listener)

    def action_scroll_categories(self, go_next):
        # type: (bool) -> None
        selected_category = scroll_values(listdir(self.PRESETS_PATH), self.selected_category, go_next)
        self.track.track_name.set_track_name(base_name=selected_category)

    def generate_base_notes(self, clip):
        # type: (Clip) -> None
        """ overridden """
        # add c3 note
        return [Note(pitch=60, velocity=127, start=0, duration=min(1, clip.length), clip=clip)]
