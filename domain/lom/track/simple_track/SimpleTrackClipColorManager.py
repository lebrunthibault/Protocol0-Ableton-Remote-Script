from collections import defaultdict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrackClips import SimpleTrackClips


class SimpleTrackClipColorManager(object):
    def __init__(self, clips, track_color):
        # type: (SimpleTrackClips, int) -> None
        self._clips = clips
        self._track_color = track_color

    def toggle_colors(self):
        # type: () -> None
        colors_on = any(c.color != self._track_color for c in list(self._clips))

        if colors_on:
            self._revert_colouring()
        else:
            self._set_colours()

    def _revert_colouring(self):
        # type: () -> None
        for clip in self._clips:
            clip.color = self._track_color

    def _set_colours(self):
        # type: () -> None
        color_index = 0

        clip_per_hash = defaultdict(list)
        for clip in self._clips:
            clip_per_hash[clip.get_hash([])].append(clip)

        for clips in clip_per_hash.values():
            for clip in clips:
                clip.color = color_index

            color_index += 1
