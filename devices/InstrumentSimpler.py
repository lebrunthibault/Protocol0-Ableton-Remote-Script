import os
from os import listdir
from os.path import join, isdir

from typing import List, Any, Optional

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.devices.presets.InstrumentPreset import InstrumentPreset
from a_protocol_0.enums.ColorEnum import ColorEnum
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.MidiClip import MidiClip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot
from a_protocol_0.utils.utils import find_if
from a_protocol_0.utils.utils import scroll_values


class InstrumentSimpler(AbstractInstrument):
    NAME = "Simpler"
    TRACK_COLOR = ColorEnum.SIMPLER
    PRESET_EXTENSION = ".wav"
    PRESETS_PATH = str(os.getenv("SAMPLE_PATH"))
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NONE
    CAN_BE_SHOWN = False

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.activated = True
        self._name_listener.subject = self.track._track

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        self.parent.log_dev("syncing presets for %s" % self)
        self.sync_presets()

    @property
    def name(self):
        # type: () -> str
        return self.selected_category if self.selected_category else "None"

    @property
    def selected_category(self):
        # type: () -> Optional[str]
        """ the name of the track is the name of a sample sub_directory """
        if not isdir(self.PRESETS_PATH):
            self.parent.log_error("Couldn't find the simpler presets path : %s" % self.PRESETS_PATH)
            return None

        selected_category = find_if(
            lambda f: self.track.base_name.split(" ")[0].strip().lower() in f.lower(), listdir(self.PRESETS_PATH)
        )
        if selected_category is None:
            self.parent.log_error("Couldn't find sample selected category for %s" % self.track)
            return None

        return str(selected_category)

    @property
    def presets_path(self):
        # type: () -> Optional[str]
        if not self.selected_category:
            return None
        else:
            return join(self.PRESETS_PATH, self.selected_category)

    def _load_preset(self, preset):
        # type: (InstrumentPreset) -> Optional[Sequence]
        self.parent.browserManager.load_sample(preset.original_name)
        self.parent._wait(400, self.track._devices_listener)
        return None

    def scroll_preset_categories(self, go_next):
        # type: (bool) -> None
        if not self.selected_category:
            self.parent.log_error("Couldn't find the selected category")
            return
        self.parent.clyphxNavigationManager.show_track_view()
        selected_category = scroll_values(listdir(self.PRESETS_PATH), self.selected_category, go_next)
        self.track.track_name.update(base_name=selected_category)

    def generate_base_notes(self, clip):
        # type: (MidiClip) -> List[Note]
        """ overridden """
        # add c3 note
        return [Note(pitch=60, velocity=127, start=0, duration=min(1, int(clip.length)), clip=clip)]
