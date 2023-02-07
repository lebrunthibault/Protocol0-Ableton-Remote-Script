from typing import List

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import (
    PresetImportInterface,
)


class NullPresetImporter(PresetImportInterface):
    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        return []
