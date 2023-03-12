from typing import cast

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipColorManager import (
    MatchingTrackClipColorManager,
)
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipsBroadcastEvent import (
    MatchingTrackClipsBroadcastEvent,
)
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackInterface import (
    MatchingTrackInterface,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.sequence.Sequence import Sequence


class ExtMatchingTrack(MatchingTrackInterface):
    def __init__(self, base_track):
        # type: (SimpleAudioTrack) -> None
        super(ExtMatchingTrack, self).__init__(base_track)
        self._midi_sub_track = cast(SimpleAudioTrack, base_track.sub_tracks[0])
        self._audio_sub_track = cast(SimpleAudioTrack, base_track.sub_tracks[1])
        # in this setup the mapping is shared between 3 audio tracks
        self._audio_track.audio_to_midi_clip_mapping.update(
            self._audio_sub_track.audio_to_midi_clip_mapping
        )
        self._audio_sub_track.audio_to_midi_clip_mapping = (
            self._audio_track.audio_to_midi_clip_mapping
        )

    @property
    def clip_color_manager(self):
        # type: () -> MatchingTrackClipColorManager
        return MatchingTrackClipColorManager(
            self.router, self._midi_sub_track, self._audio_track, self._audio_sub_track
        )

    def bounce(self):
        # type: () -> Sequence
        assert len(list(self._base_track.devices)) == 0, "Please move devices to audio track"
        assert self._base_track.devices.mixer_device.is_default, "Mixer was changed"

        bounced_clips = [
            (mc, ac)
            for (mc, ac) in zip(self._midi_sub_track.clips, self._audio_sub_track.clips)
            if ClipInfo(mc).already_bounced_to(self._audio_track)
        ]
        bounced_clips_flat = [c for clips in bounced_clips for c in clips]

        seq = Sequence()

        seq.add(self._base_track.abstract_track.arm_state.unarm)
        seq.add(self._base_track.save)
        seq.add([c.delete for c in bounced_clips_flat])
        seq.add(self._audio_sub_track.flatten)
        seq.wait_for_event(MatchingTrackClipsBroadcastEvent)
        seq.add(self._base_track.delete)

        return seq.done()
