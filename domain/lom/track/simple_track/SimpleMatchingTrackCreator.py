from functools import partial

from typing import Dict, TYPE_CHECKING

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackCreatorInterface import \
    MatchingTrackCreatorInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.lom.track.group_track.matching_track.utils import assert_valid_track_name, \
    assert_no_duplicate_midi_clip
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class SimpleMatchingTrackCreator(MatchingTrackCreatorInterface):
    def bounce(self, already_checked):
        # type: (bool) -> Sequence
        assert all(clip.looping for clip in self._base_track.clips), "Some clips are not looped"

        assert_valid_track_name(self._base_track.name)

        from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack

        if not already_checked and isinstance(self._base_track, SimpleMidiTrack):
            assert_no_duplicate_midi_clip(self._base_track)

        mixer_data = self._base_track.devices.mixer_device.to_dict()
        self._base_track.reset_mixer()

        seq = Sequence()

        seq.add(partial(self._base_track.save, check_for_duplicate=True))
        seq.add(self._base_track.flatten)
        seq.defer()

        seq.add(partial(self._post_bounce, mixer_data))
        seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _post_bounce(self, mixer_data):
        # type: (Dict) -> None
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        flattened_track = Song.selected_track(SimpleAudioTrack)
        flattened_track.devices.mixer_device.update_from_dict(mixer_data)