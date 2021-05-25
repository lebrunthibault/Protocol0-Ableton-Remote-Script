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
from a_protocol_0.lom.device.SimplerDevice import SimplerDevice
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot


class InstrumentSimpler(AbstractInstrument):
    NAME = "Simpler"
    TRACK_COLOR = ColorEnum.SIMPLER
    PRESET_EXTENSION = ".wav"
    PRESETS_PATH = str(os.getenv("SAMPLE_PATH"))
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.CATEGORY
    CAN_BE_SHOWN = False

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.activated = True
        self.device = self.device  # type: SimplerDevice
        self._name_listener.subject = self.track._track

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        self._preset_list.sync_presets()

    def _import_presets(self):
        # type: () -> None
        if self.track.base_name.lower() in (cat.lower() for cat in self.categories):
            self.selected_category = self.track.base_name
        elif self.track.base_name != self.track.DEFAULT_NAME:
            self.parent.log_error("Invalid track name, no category matched for %s" % self.track)
        super(InstrumentSimpler, self)._import_presets()

    @property
    def name(self):
        # type: () -> str
        return self.selected_category if self.selected_category else "None"

    @property
    def categories(self):
        # type: () -> List[str]
        if not isdir(self.PRESETS_PATH):
            self.parent.log_error("Couldn't find the presets path : %s for instrument %s" % (self.PRESETS_PATH, self))
            return []
        else:
            return listdir(self.PRESETS_PATH)

    @property
    def presets_path(self):
        # type: () -> Optional[str]
        if not self.selected_category:
            return None
        else:
            return join(self.PRESETS_PATH, self.selected_category)

    @property
    def preset_name(self):
        # type: () -> str
        """ overridden """
        return self.device.sample_name or "empty"

    def _load_preset(self, preset):
        # type: (InstrumentPreset) -> Optional[Sequence]
        self.parent.log_dev("preset: %s" % preset)
        self.parent.browserManager.load_sample(preset.original_name)
        self.parent._wait(400, self.track._devices_listener)
        return None

    def scroll_preset_categories(self, go_next):
        # type: (bool) -> None
        super(InstrumentSimpler, self).scroll_preset_categories(go_next=go_next)
        self.track.track_name.update(base_name=self.selected_category)

    def generate_base_notes(self, clip):
        # type: (MidiClip) -> List[Note]
        """ overridden """
        # add c3 note
        return [Note(pitch=60, velocity=127, start=0, duration=min(1, int(clip.length)), clip=clip)]
