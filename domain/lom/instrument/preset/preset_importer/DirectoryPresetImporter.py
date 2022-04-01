import os

from typing import List

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import PresetImportInterface


class DirectoryPresetImporter(PresetImportInterface):
    def __init__(self, path, preset_extension):
        # type: (str, str) -> None
        self._path = path
        self._preset_extension = preset_extension

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        presets = []  # type: List[InstrumentPreset]
        has_categories = False

        for root, dir_names, files in os.walk(self._path):
            if len(dir_names):
                has_categories = True

            if has_categories:
                if root == self._path:
                    continue

                category = root.replace(self._path + "\\", "").split("\\")[0]
                if category.startswith("_"):
                    continue
                for filename in [filename for filename in files if self._is_preset_filename(filename)]:
                    presets.append(
                        InstrumentPreset(index=len(presets), category=category, name=filename))
            else:
                for filename in [filename for filename in files if self._is_preset_filename(filename)]:
                    presets.append(InstrumentPreset(index=len(presets), name=filename))

        return presets

    def _is_preset_filename(self, filename):
        # type: (str) -> bool
        return filename.endswith(self._preset_extension) and not filename.startswith("_")
