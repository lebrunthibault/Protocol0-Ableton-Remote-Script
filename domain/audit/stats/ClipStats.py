import collections

from typing import Dict, Any

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.utils.utils import get_minutes_legend
from protocol0.shared.SongFacade import SongFacade


class ClipStats(object):
    def __init__(self):
        # type: () -> None
        self.clips = [clip for track in SongFacade.simple_tracks() for clip in track.clips]
        self.abstract_clips = []
        for track in SongFacade.abstract_tracks():
            if isinstance(track, ExternalSynthTrack):
                self.abstract_clips += track.audio_track.clips
            else:
                self.abstract_clips += track.clips

        self.audio_clips = [clip for clip in self.abstract_clips if isinstance(clip, AudioClip)]
        beat_duration = float(60) / SongFacade.tempo()

        recorded_audio_length = sum([clip.length for clip in self.audio_clips])
        self.recorded_audio_duration = recorded_audio_length * beat_duration

    def to_dict(self):
        # type: () -> Dict
        output = collections.OrderedDict()  # type: Dict[str, Any]
        output["clips count"] = len(self.clips)
        output["abstract clips count"] = len(self.abstract_clips)
        output["audio clips count"] = len(self.audio_clips)
        output["recorded audio duration"] = get_minutes_legend(self.recorded_audio_duration)

        return output
