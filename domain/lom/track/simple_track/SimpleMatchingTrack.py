from typing import Any

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipColorManager import \
    MatchingTrackClipColorManager
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipsBroadcastEvent import \
    MatchingTrackClipsBroadcastEvent
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackInterface import (
    MatchingTrackInterface,
)
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.utils.utils import assert_valid_track_name
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

    def bounce(self):
        # type: () -> Sequence
        assert all(
            clip.looping for clip in self._base_track.clips
        ), "Some clips are not looped"
        assert self._base_track.devices.mixer_device.is_default, "Mixer was changed"

        assert_valid_track_name(self._base_track.name)

        # keep the midi / audio link even on midi clip update
        if isinstance(self._base_track, SimpleMidiTrack):
            for clip in self._base_track.clips:
                if clip.previous_midi_hash != clip.midi_hash:
                    self._audio_track.audio_to_midi_clip_mapping.register_midi_hash_equivalence(
                        clip.previous_midi_hash, clip.midi_hash
                    )
                    clip.previous_midi_hash = clip.midi_hash

        seq = Sequence()

        seq.add(self._base_track.save)
        seq.add(self._base_track.flatten)
        seq.wait_for_event(MatchingTrackClipsBroadcastEvent)
        seq.add(self._base_track.delete)

        return seq.done()
