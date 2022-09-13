from typing import List

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import (
    DirectoryPresetImporter,
)
from protocol0.domain.lom.sample.SampleCategoryEnum import SampleCategoryEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade


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
    def suffix(self):
        # type: () -> str
        return self.name.split(" ")[0].lower()

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
        return DirectoryPresetImporter(self._sample_directory, ".wav").import_presets()

    @property
    def live_presets(self):
        # type: () -> List[InstrumentPreset]
        return DirectoryPresetImporter(self._sample_directory, ".wav").import_presets(
            use_cache=False
        )

    @property
    def create_track_index(self):
        # type: () -> int
        assert self._category.parent_track is not None, "Sample group track doesn't exist"
        sample_tracks = self._category.parent_track.get_all_simple_sub_tracks()

        def index_from_track(matched_track):
            # type: (SimpleTrack) -> int
            if sample_tracks[-1] == matched_track:
                return sample_tracks[-1].index
            else:
                return matched_track.index + 1

        # we clicked on a track means : we add to the right
        if self._category.parent_track in SongFacade.selected_track().group_tracks:
            return index_from_track(SongFacade.selected_track())

        # match by category
        same_category_track = find_if(
            lambda t: t.name.lower() == self.name.lower(), reversed(sample_tracks)
        )
        if same_category_track:
            return index_from_track(same_category_track)

        # match by prefix
        for track in reversed(sample_tracks):
            if track.name.split(" ")[0].lower() == self.suffix:
                return index_from_track(track)

        # -1 sometimes doesn't create it in the drum group
        return sample_tracks[-2].index if len(sample_tracks) > 1 else 0
