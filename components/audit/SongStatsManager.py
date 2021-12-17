import collections
import json

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack


class SongStatsManager(AbstractControlSurfaceComponent):
    def display_song_stats(self):
        # type: () -> None
        stats = self._get_stats()
        # self.parent.logManager.clear()
        self.parent.log_info(json.dumps(stats, indent=4))

    def _get_stats(self):
        # type: () -> collections.OrderedDict

        song_clips = [cs.clip for cs in self.song.live_clip_slot_to_clip_slot.values() if cs.clip]
        audio_recorded_clips = [clip for clip in song_clips if
                                isinstance(clip, AudioClip) and clip.track.__class__ not in
                                (SimpleInstrumentBusTrack, SimpleAudioTailTrack, SimpleDummyTrack)]

        self.parent.log_dev("audio_recorded_clips: %s" % audio_recorded_clips)
        abstract_clip_count = 0
        for track in self.song.abstract_tracks:
            if isinstance(track, ExternalSynthTrack):
                abstract_clip_count += len(track.audio_track.clips)
            else:
                abstract_clip_count += len(track.clips)

        stats = collections.OrderedDict()
        stats["clipCount"] = len(song_clips)
        stats["abstractClipCount"] = abstract_clip_count
        stats["audioRecordClipCount"] = len(audio_recorded_clips)
        stats["sceneCount"] = len(self.song.scenes)
        stats["trackCount"] = len(list(self.song.simple_tracks))
        stats["abstractTrackCount"] = len(
            [track for track in self.song.abstract_tracks if not isinstance(track, NormalGroupTrack)])
        stats["extSynthTrackCount"] = len(list(self.song.external_synth_tracks))
        stats["devicesCount"] = sum([len(track.devices) for track in self.song.simple_tracks])

        return stats
