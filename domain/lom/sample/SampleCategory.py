from typing import List, Optional

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import (
    DirectoryPresetImporter,
)
from protocol0.domain.lom.sample.SampleCategoryEnum import SampleCategoryEnum
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.VocalsTrack import VocalsTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song


class SampleCategory(object):
    """
        Represents a sample folder that can be loaded in one click in a drum rack

        Used to access my library easily
    """
    def __init__(self, category, name):
        # type: (SampleCategoryEnum, str) -> None
        self._category = category
        self._name = name

    def __repr__(self):
        # type: () -> str
        return "SampleCategory(category=%s, name=%s)" % (self._category, self._name)

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def color(self):
        # type: () -> int
        return self._parent_track.color

    @property
    def _sample_directory(self):
        # type: () -> str
        return "%s\\%s" % (self._category.sample_directory, self._name)

    @property
    def drum_rack_name(self):
        # type: () -> str
        return "%s %s.adg" % (self._category.drum_rack_prefix, self._name.title())

    @property
    def presets(self):
        # type: () -> List[InstrumentPreset]
        return DirectoryPresetImporter(self._sample_directory).import_presets()

    @property
    def live_presets(self):
        # type: () -> List[InstrumentPreset]
        return DirectoryPresetImporter(self._sample_directory).import_presets(
            use_cache=False
        )

    @property
    def create_track_index(self):
        # type: () -> int
        assert self._parent_track is not None, "Sample group track doesn't exist"
        sample_tracks = self._parent_track.get_all_simple_sub_tracks()

        def index_from_track(matched_track):
            # type: (SimpleTrack) -> int
            if matched_track.is_foldable:
                return index_from_track(matched_track.sub_tracks[-1])

            if sample_tracks[-1] == matched_track:
                return sample_tracks[-1].index
            else:
                return matched_track.index + 1

        # we clicked on a track means : we add to the right
        if self._parent_track in Song.selected_track().group_tracks:
            return index_from_track(Song.selected_track())
        else:
            return index_from_track(self._parent_track.sub_tracks[0].base_track)

    @property
    def _parent_track(self):
        # type: () -> Optional[AbstractGroupTrack]
        if self._category == SampleCategoryEnum.VOCALS and Song.vocals_track() is None:
            Backend.client().show_warning(
                "Couldn't find %s track. Using drums track instead" % VocalsTrack.TRACK_NAME
            )
            return Song.drums_track()

        return {
                SampleCategoryEnum.DRUMS: Song.drums_track(),
                SampleCategoryEnum.VOCALS: Song.vocals_track(),
            }[self._category]
