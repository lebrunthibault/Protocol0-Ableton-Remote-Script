import collections
import datetime
import json
from collections import OrderedDict

from typing import Union

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class SongStatsService(object):
    def display_song_stats(self):
        # type: () -> None
        stats = self._get_stats()
        Logger.clear()
        Logger.log_info(json.dumps(stats, indent=4))

    def _get_stats(self):
        # type: () -> collections.OrderedDict
        song_clips = [clip for track in SongFacade.simple_tracks() for clip in track.clips]
        audio_recorded_clips = [clip for clip in song_clips if
                                isinstance(clip, AudioClip) and clip.track.__class__ not in
                                (SimpleInstrumentBusTrack, SimpleAudioTailTrack, SimpleDummyTrack)]

        beat_duration = float(60) / SongFacade.tempo()
        recorded_audio_length = sum([clip.length for clip in audio_recorded_clips])
        recorded_audio_duration = recorded_audio_length * beat_duration
        song_duration = sum([scene.length for scene in SongFacade.scenes()]) * beat_duration

        abstract_clip_count = 0
        for track in SongFacade.abstract_tracks():
            if isinstance(track, ExternalSynthTrack):
                abstract_clip_count += len(track.audio_track.clips)
            else:
                abstract_clip_count += len(track.clips)

        stats = collections.OrderedDict()   # type: OrderedDict[str, Union[int, str]]
        stats["clipCount"] = len(song_clips)
        stats["abstractClipCount"] = abstract_clip_count
        stats["audioRecordClipCount"] = len(audio_recorded_clips)
        stats["sceneCount"] = len(SongFacade.scenes())
        stats["trackCount"] = len(list(SongFacade.simple_tracks()))
        stats["abstractTrackCount"] = len(
            [track for track in SongFacade.abstract_tracks() if not isinstance(track, NormalGroupTrack)])
        stats["extSynthTrackCount"] = len(list(SongFacade.external_synth_tracks()))
        stats["devicesCount"] = sum([len(track.devices) for track in SongFacade.simple_tracks()])
        stats["recordedAudioDuration"] = str(datetime.timedelta(seconds=round(recorded_audio_duration)))
        stats["sessionSongDuration"] = str(datetime.timedelta(seconds=round(song_duration)))

        return stats