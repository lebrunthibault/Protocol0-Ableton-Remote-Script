import os

from typing import List, Optional

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import (
    PresetImportInterface,
)


class DirectoryPresetImporter(PresetImportInterface):
    def __init__(self, path, extension=None):
        # type: (str, Optional[str]) -> None
        self._path = path
        if extension is not None:
            self._extensions = [extension]
        else:
            self._extensions = [".wav", ".aif"]

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        presets = []  # type: List[InstrumentPreset]
        has_categories = False

        for root, dir_names, files in os.walk(self._path):
            if len(dir_names):
                has_categories = True

            if has_categories:
                if root == self._path:
                    category = "unclassified"
                else:
                    category = root.replace(self._path + "\\", "").split("\\")[0]

                if category.startswith("_"):
                    continue
                for filename in [
                    filename for filename in files if self._is_preset_filename(filename)
                ]:
                    presets.append(
                        InstrumentPreset(index=len(presets), category=category, name=filename)
                    )
            else:
                for filename in [
                    filename for filename in files if self._is_preset_filename(filename)
                ]:
                    presets.append(InstrumentPreset(index=len(presets), name=filename))

        return presets

    def _is_preset_filename(self, filename):
        # type: (str) -> bool
        if filename.startswith("_"):
            return False

        return any(filename.endswith(ext) for ext in self._extensions)
