from typing import Tuple, Optional, TYPE_CHECKING, cast

from protocol0.domain.lom.track.group_track.dummy_group.DummyGroup import DummyGroup
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
        ExternalSynthTrack,
    )


class ExternalSynthTrackDummyGroup(DummyGroup):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        super(ExternalSynthTrackDummyGroup, self).__init__(track)
        self._track = track

    def _get_tracks(self):
        # type: () -> Tuple[Optional[SimpleAudioTrack], Optional[SimpleAudioTrack]]
        main_tracks_length = 3 if self._track.audio_tail_track else 2

        if len(self._track.sub_tracks) == main_tracks_length + 2:
            assert isinstance(self._track.sub_tracks[-2], SimpleAudioTrack)
            assert isinstance(self._track.sub_tracks[-1], SimpleAudioTrack)
            return cast(SimpleAudioTrack, self._track.sub_tracks[-2]), cast(
                SimpleAudioTrack, self._track.sub_tracks[-1]
            )
        if len(self._track.sub_tracks) >= main_tracks_length + 1:
            assert isinstance(self._track.sub_tracks[-1], SimpleAudioTrack)
            dummy_track = cast(SimpleAudioTrack, self._track.sub_tracks[-1])
            # is it the dummy return track ?
            if self._track.sub_tracks[-1].output_routing.type == OutputRoutingTypeEnum.SENDS_ONLY:
                return None, dummy_track
            else:
                return dummy_track, None

        return None, None

    def loop_if_tail(self, scene_index, clip_bar_length):
        # type: (int, float) -> None
        """Loop the dummy clip in the special case it contains a tail but should play it only later"""
        for dummy_track in filter(None, (self._dummy_track, self._dummy_return_track)):
            dummy_clip = dummy_track.clip_slots[scene_index].clip
            if (
                dummy_clip is not None
                and dummy_clip.has_tail(clip_bar_length)
                and dummy_clip.playing_position.bars_left < clip_bar_length
            ):
                dummy_clip.fire()
