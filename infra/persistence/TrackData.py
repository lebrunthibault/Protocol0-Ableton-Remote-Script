from typing import TYPE_CHECKING, Dict

from protocol0.domain.lom.track.simple_track.AudioToMidiClipMapping import AudioToMidiClipMapping
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
                TrackDataEnum.CLIP_MAPPING.value,
                self._track.clip_mapping.to_dict(),
            )

    def restore(self):
        # type: () -> None
        # noinspection PyTypeChecker
        mapping_data = self._track._track.get_data(
            TrackDataEnum.CLIP_MAPPING.value, None
        )  # type: Dict

        if mapping_data is not None:
            self._track.clip_mapping = AudioToMidiClipMapping(self, mapping_data)
