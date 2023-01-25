from typing import Any

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
        self._track_proxy.base_track.reset_mixer()

    def bounce(self):
        # type: () -> Sequence
        assert all(
            clip.looping for clip in self._track_proxy.base_track.clips
        ), "Some clips are not looped"
        assert self._track_proxy.base_track.devices.mixer_device.is_default, "Mixer was changed"

        assert_valid_track_name(self._track_proxy.base_track.name)

        # keep the midi / audio link even on midi clip update
        if isinstance(self._track_proxy.base_track, SimpleMidiTrack):
            for clip in self._track_proxy.base_track.clips:
                if clip.previous_midi_hash != clip.midi_hash:
                    self._track_proxy.audio_track.audio_to_midi_clip_mapping.register_midi_hash_equivalence(
                        clip.previous_midi_hash, clip.midi_hash
                    )
                    clip.previous_midi_hash = clip.midi_hash

        seq = Sequence()

        seq.add(self._track_proxy.base_track.save)
        seq.add(self._track_proxy.base_track.flatten)
        seq.add(self._track_proxy.base_track.delete)

        return seq.done()
