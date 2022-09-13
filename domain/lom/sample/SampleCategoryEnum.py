from typing import Optional, List

from protocol0.domain.lom.instrument.instrument.InstrumentSimpler import InstrumentSimpler
from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import (
    DirectoryPresetImporter,
)
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.VocalsTrack import VocalsTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade


class SampleCategoryEnum(AbstractEnum):
    DRUMS = "DRUMS"
    VOCALS = "VOCALS"

    @property
    def sample_directory(self):
        # type: () -> str
        return self.get_value_from_mapping(
            {
                SampleCategoryEnum.DRUMS: Config.SAMPLE_DIRECTORY,
                SampleCategoryEnum.VOCALS: "%s\\Vocal" % Config.SAMPLE_DIRECTORY,
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
    def parent_track(self):
        # type: () -> Optional[AbstractGroupTrack]
        if self == SampleCategoryEnum.VOCALS and SongFacade.vocals_track() is None:
            Backend.client().show_warning(
                "Couldn't find %s track. Using drums track instead" % VocalsTrack.TRACK_NAME
            )
            return SongFacade.drums_track()

        return self.get_value_from_mapping(
            {
                SampleCategoryEnum.DRUMS: SongFacade.drums_track(),
                SampleCategoryEnum.VOCALS: SongFacade.vocals_track(),
            }
        )

    @property
    def subcategories(self):
        # type: () -> List[str]
        subcategories = set()

        presets = DirectoryPresetImporter(
            self.sample_directory, InstrumentSimpler.PRESET_EXTENSION
        ).import_presets()
        for preset in presets:
            subcategories.add(preset.category)

        return sorted(subcategories)
