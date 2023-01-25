import json
from collections import defaultdict
from os.path import basename

from typing import List, Dict, TYPE_CHECKING, cast

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.infra.persistence.TrackData import TrackData


class AudioToMidiClipMapping(object):
    """
        Keep a reference to audio clips midi origin as a midi hash
        to be able to update audio clips on midi clip change and rerecording
        hash to file path is a many to many relationship
    """

    _DEBUG = True

    def __init__(self, track_data, file_path_mapping=None, midi_hash_equivalences=None):
        # type: (TrackData, Dict[str, int], Dict[int, List[int]]) -> None
        self._track_data = track_data
        self._file_path_mapping = file_path_mapping or {}  # type: Dict[str, int]
        self._midi_hash_equivalences = defaultdict(list)  # type: Dict[int, List[int]]

        if midi_hash_equivalences is not None:
            self._midi_hash_equivalences.update(midi_hash_equivalences)

    def __repr__(self):
        # type: () -> str
        return json.dumps(self.to_dict(), indent=4)

    def to_dict(self):
        # type: () -> Dict
        return {
            "file_path_mapping": self._file_path_mapping,
            "midi_hash_equivalences": self._midi_hash_equivalences
        }


    @classmethod
    def from_dict(cls, track_data, data):
        # type: (TrackData, Dict) -> AudioToMidiClipMapping
        midi_hash_equivalences = {int(k): v for k, v in data["midi_hash_equivalences"].items()}

        return AudioToMidiClipMapping(track_data, data["file_path_mapping"], midi_hash_equivalences)

    def update(self, other_mapping):
        # type: (AudioToMidiClipMapping) -> None
        self._file_path_mapping.update(other_mapping._file_path_mapping)

        for midi_hash, equivalences in other_mapping._midi_hash_equivalences.items():
            self._midi_hash_equivalences[midi_hash] += equivalences
            # keep unique values
            self._midi_hash_equivalences[midi_hash] = list(set(self._midi_hash_equivalences[midi_hash]))

    def register_file_path(self, file_path, clip_info):
        # type: (str, ClipInfo) -> None
        midi_hash = clip_info.midi_hash
        if midi_hash is None:
            midi_hash = self._file_path_mapping.get(cast(str, clip_info.file_path), None)

        assert midi_hash is not None, "The clip info file path was not recognized"

        if self._DEBUG:
            Logger.info("register %s -> %s" % (basename(file_path), midi_hash))

        self._file_path_mapping[file_path] = midi_hash
        if midi_hash not in self._midi_hash_equivalences:
            self._midi_hash_equivalences[midi_hash] = [midi_hash]
        self._track_data.save()

    def register_midi_hash_equivalence(self, existing_hash, new_hash):
        # type: (int, int) -> None
        if self._DEBUG:
            Logger.info("register %s -> %s" % (existing_hash, new_hash))

        hash_list = self._midi_hash_equivalences.get(existing_hash, [])
        hash_list.append(new_hash)
        self._midi_hash_equivalences[new_hash] = hash_list
        self._midi_hash_equivalences[existing_hash] = hash_list

    def hash_matches_file_path(self, midi_hash, file_path):
        # type: (int, str) -> bool
        if file_path not in self._file_path_mapping:
            return False

        file_path_midi_hash = self._file_path_mapping[file_path]
        return midi_hash in self._midi_hash_equivalences[file_path_midi_hash]

    def file_path_matches_file_path(self, file_path_1, file_path_2):
        # type: (str, str) -> bool
        midi_hash_1 = self._file_path_mapping.get(file_path_1, None)

        return midi_hash_1 is not None and self.hash_matches_file_path(midi_hash_1, file_path_2)
