from typing import TYPE_CHECKING, Dict, cast, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.infra.persistence.TrackDataEnum import TrackDataEnum

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class TrackData(object):
    def __init__(self, track):
        # type: (SimpleAudioTrack) -> None
        self._track = track
        self._file_path_mapping = {}  # type: Dict[str, int]

    def save(self):
        # type: () -> None
        clips_data = [clip.to_dict() for clip in self._track.clips]

        self._track._track.set_data(TrackDataEnum.CLIPS.value, clips_data)
        self._track._track.set_data(
            TrackDataEnum.FILE_PATH_MAPPING.value, self._track._file_path_mapping
        )

    def restore(self):
        # type: () -> None
        self._track._file_path_mapping = self._track._track.get_data(
            TrackDataEnum.FILE_PATH_MAPPING.value, {}
        )
        clips_data = cast(
            Optional[Dict], self._track._track.get_data(TrackDataEnum.CLIPS.value, None)
        )

        if clips_data is None:
            return

        track_clips = {clip.index: clip for clip in self._track.clips}  # type: Dict[int, AudioClip]

        for clip_info in clips_data:
            if clip_info.get("index", None) in track_clips:
                audio_clip = track_clips[clip_info["index"]]
                audio_clip.update_from_dict(clip_info)
