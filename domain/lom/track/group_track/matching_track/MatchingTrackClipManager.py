from functools import partial

from typing import Optional, List

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackRouter import (
    MatchingTrackRouter,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.sequence.Sequence import Sequence


class MatchingTrackClipManager(object):
    def __init__(self, router, base_track, audio_track):
        # type: (MatchingTrackRouter, SimpleTrack, SimpleAudioTrack) -> None
        self._router = router
        self._base_track = base_track
        self._audio_track = audio_track
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        # merge the file path mapping into one reference
        if isinstance(self._base_track, SimpleAudioTrack):
            self._audio_track.clip_mapping.update(self._base_track.clip_mapping)
            self._base_track.clip_mapping = self._audio_track.clip_mapping

    def broadcast_clips(self, flattened_track, clip_infos):
        # type: (SimpleAudioTrack, List[ClipInfo]) -> Optional[Sequence]
        audio_track = self._audio_track

        seq = Sequence()

        for clip_info in clip_infos:
            seq.add(partial(self._broadcast_clip, clip_info, flattened_track))

        def post_broadcast():
            # type: () -> None
            replaced_cs = [cs for c in clip_infos for cs in c.replaced_clip_slots]

            if len(replaced_cs) == 0:
                Backend.client().show_warning("No clip replaced")
            else:
                message = "%s / %s clips replaced" % (len(replaced_cs), len(audio_track.clips))
                Backend.client().show_success(message, centered=True)

            self._router.monitor_audio_track()
            # in case the base track is not already removed
            Scheduler.wait_ms(1500, self._router.monitor_base_track)

            for cs in replaced_cs:
                cs.clip.blink()

        seq.add(post_broadcast)

        return seq.done()

    def _broadcast_clip(self, clip_info, source_track):
        # type:  (ClipInfo, SimpleAudioTrack) -> Optional[Sequence]
        source_cs = source_track.clip_slots[clip_info.index]
        assert source_cs.clip is not None, "Couldn't find clip at index %s" % clip_info.index

        matching_clip_slots = clip_info.matching_clip_slots(self._audio_track)
        clip_info.replaced_clip_slots = matching_clip_slots

        # new clip
        if len(matching_clip_slots) == 0:
            dest_cs = self._audio_track.clip_slots[source_cs.index]

            if dest_cs.clip is not None:
                dest_cs = find_if(lambda c: c.clip is None, self._audio_track.clip_slots)  # type: ignore

            assert dest_cs is not None, (
                "Expected empty clip slot for copying %s. Please create scene" % source_cs
            )

            clip_info.replaced_clip_slots = [dest_cs]

            return source_cs.duplicate_clip_to(dest_cs)

        seq = Sequence()
        for dest_cs in matching_clip_slots:
            seq.add(partial(self._audio_track.replace_clip_sample, dest_cs, source_cs))

        seq.add(Backend.client().close_samples_windows)

        return seq.done()
