from typing import TYPE_CHECKING

from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.infra.persistence.TrackDataEnum import TrackDataEnum

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class TrackData(object):
    def __init__(self, track):
        # type: (SimpleAudioTrack) -> None
        self._track = track

    def __repr__(self):
        # type: () -> str
        return "TrackData(%s)" % self._track

    def save(self):
        # type: () -> None
        if liveobj_valid(self._track._track):
            self._track._track.set_data(
                TrackDataEnum.FILE_PATH_MAPPING.value, self._track.file_path_mapping
            )

    def restore(self):
        # type: () -> None
        self._track.file_path_mapping = self._track._track.get_data(
            TrackDataEnum.FILE_PATH_MAPPING.value, {}
        )
