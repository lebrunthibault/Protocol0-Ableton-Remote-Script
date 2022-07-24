import os

from typing import List

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import (
    DirectoryPresetImporter,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade


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

    @property
    def suffix(self):
        # type: () -> str
        return self.name.split(" ")[0].lower()

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
        return DirectoryPresetImporter(self._sample_directory, ".wav").import_presets(
            use_cache=False
        )

    @property
    def uses_scene_length_clips(self):
        # type: () -> bool
        return self.name.lower() in ["crash", "fill", "glitch", "impact", "perc", "reverse", "riser", "texture"]

    @property
    def create_track_index(self):
        # type: () -> int
        assert SongFacade.drums_track() is not None, "Drum track doesn't exist"
        drum_tracks = SongFacade.drums_track().get_all_simple_sub_tracks()

        def index_from_track(matched_track):
            # type: (SimpleTrack) -> int
            if drum_tracks[-1] == matched_track:
                return drum_tracks[-1].index
            else:
                return matched_track.index + 1

        # we clicked on a track means : we add to the right
        if SongFacade.drums_track() in SongFacade.selected_track().group_tracks:
            return index_from_track(SongFacade.selected_track())

        # match by category
        same_category_track = find_if(
            lambda t: t.name.lower() == self.name.lower(), reversed(drum_tracks)
        )
        if same_category_track:
            return index_from_track(same_category_track)

        # match by prefix
        for track in reversed(drum_tracks):
            if track.name.split(" ")[0].lower() == self.suffix:
                return index_from_track(track)

        # -1 sometimes doesn't create it in the drum group
        return drum_tracks[-2].index if len(drum_tracks) > 1 else 0
