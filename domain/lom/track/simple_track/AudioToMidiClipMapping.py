import json
from os.path import basename

from typing import List, Dict, TYPE_CHECKING

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.infra.persistence.TrackData import TrackData


class AudioToMidiClipMapping(object):
    """
    Keep a reference to audio clips origin as a list of hashes
    to be able to update audio clips on source clip change and rerecording
    hash to file path is a many to many relationship
    """

    _DEBUG = False

    def __init__(self, track_data, file_path_mapping=None):
        # type: (TrackData, Dict[str, List[int]]) -> None
        self._track_data = track_data
        self._file_path_mapping = file_path_mapping or {}  # type: Dict[str, List[int]]

    def __repr__(self):
        # type: () -> str
        return json.dumps({basename(k): v for k, v in self._file_path_mapping.items()}, indent=4)

    def to_dict(self):
        # type: () -> Dict
        return self._file_path_mapping

    def update(self, other_mapping):
        # type: (AudioToMidiClipMapping) -> None
        for file_path, equivalences in other_mapping._file_path_mapping.items():
            for clip_hash in equivalences:
                if file_path not in self._file_path_mapping:
                    self._file_path_mapping[file_path] = []

                if clip_hash not in self._file_path_mapping[file_path]:
                    self._file_path_mapping[file_path].append(clip_hash)

    def register_file_path(self, file_path, clip_info):
        # type: (str, ClipInfo) -> None
        if self._DEBUG:
            Logger.info("register %s -> %s" % (basename(file_path), clip_info.hash))

        if file_path not in self._file_path_mapping:
            self._file_path_mapping[file_path] = []

        if clip_info.hash not in self._file_path_mapping[file_path]:
            self._file_path_mapping[file_path].append(clip_info.hash)

        self._track_data.save()

    def register_hash_equivalence(self, existing_hash, new_hash):
        # type: (int, int) -> None
        if self._DEBUG:
            Logger.info("registering equivalence: %s -> %s" % (existing_hash, new_hash))

        for equivalences in self._file_path_mapping.values():
            if existing_hash in equivalences and new_hash not in equivalences:
                equivalences.append(new_hash)

    def path_matches_hash(self, file_path, clip_hash, exact):
        # type: (str, int, bool) -> bool
        if file_path not in self._file_path_mapping:
            return False

        equivalences = self._file_path_mapping.get(file_path, [])

        # exact will not check previous versions
        if exact:
            return clip_hash == next(iter(equivalences), None)
        else:
            return clip_hash in equivalences
