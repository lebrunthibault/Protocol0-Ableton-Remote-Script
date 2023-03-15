from typing import Any, Optional

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipColorManager import (
    MatchingTrackClipColorManager,
)
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackInterface import (
    MatchingTrackInterface,
)
from protocol0.domain.lom.track.group_track.matching_track.utils import assert_valid_track_name
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMatchingTrack(MatchingTrackInterface):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMatchingTrack, self).__init__(*a, **k)
        # clean the mixer if necessary (e.g. when loading back a midi track for the 1st time)
        self._base_track.reset_mixer()

    @property
    def clip_color_manager(self):
        # type: () -> MatchingTrackClipColorManager
        return MatchingTrackClipColorManager(self.router, self._base_track, self._audio_track)

    def init_clips(self):
        # type: () -> None
        for clip in self._base_track.clips:
            clip.previous_hash = clip.get_hash(self._base_track.devices.parameters)

    def bounce(self):
        # type: () -> Optional[Sequence]
        assert all(clip.looping for clip in self._base_track.clips), "Some clips are not looped"
        assert self._base_track.devices.mixer_device.is_default, "Mixer was changed"

        assert_valid_track_name(self._base_track.name)

        # maintain hash / path link on hash change (update)
        for clip in self._base_track.clips:
            clip_hash = clip.get_hash(self._base_track.devices.parameters)
            if clip.previous_hash == clip_hash:
                continue

            self._audio_track.clip_mapping.register_hash_equivalence(
                clip.previous_hash, clip_hash
            )
            clip.previous_hash = clip_hash

        bounced_clips = [
            c
            for c in self._base_track.clips
            if ClipInfo(c, self._base_track.devices.parameters).already_bounced_to(
                self._audio_track
            )
        ]

        if bounced_clips == self._base_track.clips:
            Backend.client().show_success("No new clip to bounce")
            return None

        elif len(bounced_clips) != 0:
            Logger.info("Removing bounced clips: %s" % bounced_clips)

        seq = Sequence()
        seq.add(self._base_track.save)
        seq.add([c.delete for c in bounced_clips])
        seq.add(self._base_track.flatten)
        seq.add(lambda: Song.selected_track().delete())

        return seq.done()
