import os
from os.path import isfile, isdir

from typing import TYPE_CHECKING, List, Optional, Any

from a_protocol_0.devices.presets.InstrumentPreset import InstrumentPreset
from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentPresetList(AbstractObject):
    def __init__(self, instrument, *a, **k):
        # type: (AbstractInstrument, Any, Any) -> None
        super(InstrumentPresetList, self).__init__(*a, **k)
        self.instrument = instrument
        self.has_preset_names = False
        self.presets = []  # type: List[InstrumentPreset]
        self.selected_preset = None  # type: Optional[InstrumentPreset]
        self.sync_presets()

    def __repr__(self):
        # type: () -> str
        return "preset count: %d, selected preset: %s" % (len(self.presets), self.selected_preset)

    def sync_presets(self):
        # type: () -> None
        self.presets = self._import_presets()
        self.selected_preset = self._get_selected_preset()

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        presets = []
        presets_path = self.instrument.presets_path
        if not presets_path:
            return [
                InstrumentPreset(instrument=self.instrument, index=i)
                for i in range(0, self.instrument.NUMBER_OF_PRESETS)
            ]

        self.has_preset_names = True
        if isfile(presets_path):
            return [
                InstrumentPreset(instrument=self.instrument, index=i, name=name)
                for i, name in enumerate(open(presets_path).readlines())
            ]
        elif isdir(presets_path):
            for _, _, files in os.walk(presets_path):
                for file in [file for file in files if file.endswith(self.instrument.PRESET_EXTENSION)]:
                    presets.append(InstrumentPreset(instrument=self.instrument, index=len(presets), name=file))

            return presets

        self.parent.log_error("Couldn't import presets for %s" % self.instrument)
        return []

    def _get_selected_preset(self):
        # type: () -> InstrumentPreset
        """
        Checking first the device name (e.g. simpler)
        then the track name (Serum or Minitaur)
        then the track selected index (prophet)
        """

        def find_by_name(name):
            # type: (str) -> Optional[InstrumentPreset]
            for preset in self.presets:
                if preset.name == name:
                    return preset

            return None

        return (
            find_by_name(self.instrument.preset_name)
            or find_by_name(self.instrument.track.abstract_track.name)
            or self.presets[self.instrument.track.abstract_track.track_name.selected_preset_index]
        )

    def scroll(self, go_next):
        # type: (bool) -> None
        new_preset_index = self.selected_preset.index + (1 if go_next else -1)
        self.selected_preset = self.presets[new_preset_index % len(self.presets)]
