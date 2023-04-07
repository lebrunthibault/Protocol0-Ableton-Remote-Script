from typing import Optional

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackRouter import (
    MatchingTrackRouter,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class MatchingTrackClipColorManager(object):
    def __init__(self, router, clip_track, audio_track, audio_track_2=None):
        # type: (MatchingTrackRouter, SimpleTrack, SimpleAudioTrack, Optional[SimpleAudioTrack]) -> None
        self._router = router
        self._clip_track = clip_track
        self._audio_track = audio_track
        self._audio_track_2 = audio_track_2

    def toggle_clip_colors(self):
        # type: () -> None
        colors_on = any(c.color != self._clip_track.color for c in self._clip_track.clips)

        if colors_on:
            self._revert_colouring()
        else:
            self._set_colours()

    def _revert_colouring(self):
        # type: () -> None
        self._router.monitor_base_track()
        clips = self._clip_track.clips + self._audio_track.clips
        if self._audio_track_2 is not None:
            clips += self._audio_track_2.clips

        for clip in clips:
            clip.color = self._clip_track.color

    def _set_colours(self):
        # type: () -> None
        self._router.monitor_audio_track()  # show clip colors

        color_index = 0
        clip_infos = ClipInfo.create_from_clips(
            self._clip_track.clips, self._clip_track.devices.parameters
        )

        for clip_info in clip_infos:
            clips = clip_info.get_clips(self._clip_track.clip_slots)
            for clip in clips:
                clip.color = color_index

            for cs in clip_info.matching_clip_slots(self._audio_track):
                cs.clip.color = color_index

            color_index += 1
