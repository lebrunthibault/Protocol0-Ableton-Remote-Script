from typing import List

from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import (
    DirectoryPresetImporter,
)
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Config import Config


class SampleCategoryEnum(AbstractEnum):
    DRUMS = "DRUMS"
    VOCALS = "VOCALS"

    @property
    def sample_directory(self):
        # type: () -> str
        return self.get_value_from_mapping(
            {
                SampleCategoryEnum.DRUMS: Config.SAMPLE_DIRECTORY,
                SampleCategoryEnum.VOCALS: "%s\\_Vocal" % Config.SAMPLE_DIRECTORY,
            }
        )

    @property
    def drum_rack_prefix(self):
        # type: () -> str
        return self.get_value_from_mapping(
            {
                SampleCategoryEnum.DRUMS: "DR",
                SampleCategoryEnum.VOCALS: "V",
            }
        )

    @property
    def subcategories(self):
        # type: () -> List[str]
        subcategories = set()

        presets = DirectoryPresetImporter(self.sample_directory).import_presets()
        for preset in presets:
            subcategories.add(preset.category)

        return sorted(subcategories)
