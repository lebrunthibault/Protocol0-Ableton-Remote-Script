from typing import List

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import (
    PresetImportInterface,
)


class FilePresetImporter(PresetImportInterface):
    def __init__(self, path):
        # type: (str) -> None
        self._path = path

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        return [
            InstrumentPreset(index=i, name=name)
            for i, name in enumerate(open(self._path).readlines()[0:128])
        ]
