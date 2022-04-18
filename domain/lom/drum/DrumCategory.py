import os

from typing import List

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import DirectoryPresetImporter
from protocol0.shared.Config import Config


class DrumCategory(object):
    def __init__(self, name):
        # type: (str) -> None
        self._name = name

    def __repr__(self):
        # type: () -> str
        return "DrumCategory(name=%s)" % self._name

    @property
    def name(self):
        # type: () -> str
        return self._name

    @classmethod
    def all(cls):
        # type: () -> List[str]
        return [d.lower() for d in os.listdir(Config.SAMPLE_DIRECTORY) if not d.startswith("_")]

    @property
    def _sample_directory(self):
        # type: () -> str
        return "%s\\%s" % (Config.SAMPLE_DIRECTORY, self._name)

    @property
    def drum_rack_name(self):
        # type: () -> str
        return "DR %s.adg" % self._name.title()

    @property
    def presets(self):
        # type: () -> List[InstrumentPreset]
        return DirectoryPresetImporter(self._sample_directory, ".wav").import_presets()

    @property
    def live_presets(self):
        # type: () -> List[InstrumentPreset]
        return DirectoryPresetImporter(self._sample_directory, ".wav").import_presets(use_cache=False)
