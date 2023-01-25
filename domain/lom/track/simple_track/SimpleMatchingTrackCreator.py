from functools import partial

from typing import Dict, TYPE_CHECKING

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackCreatorInterface import \
    MatchingTrackCreatorInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.utils.utils import assert_valid_track_name
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class SimpleMatchingTrackCreator(MatchingTrackCreatorInterface):
    def bounce(self):
        # type: () -> Sequence
        assert all(clip.looping for clip in self._base_track.clips), "Some clips are not looped"
        assert_valid_track_name(self._base_track.name)

        mixer_data = self._base_track.devices.mixer_device.to_dict()  # type: ignore
        self._base_track.reset_mixer()

        seq = Sequence()

        seq.add(self._base_track.save)
        seq.add(self._base_track.flatten)

        seq.add(partial(self._post_bounce, mixer_data))
        seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _post_bounce(self, mixer_data):
        # type: (Dict) -> None
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        flattened_track = Song.selected_track(SimpleAudioTrack)
        flattened_track.devices.mixer_device.update_from_dict(mixer_data)  # type: ignore