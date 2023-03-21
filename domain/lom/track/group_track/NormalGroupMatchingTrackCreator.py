from functools import partial

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackCreatorInterface import (
    MatchingTrackCreatorInterface,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.lom.track.group_track.matching_track.utils import assert_valid_track_name
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class NormalGroupMatchingTrackCreator(MatchingTrackCreatorInterface):
    def bounce(self):
        # type: () -> Sequence
        assert_valid_track_name(self._base_track.name)

        # noinspection DuplicatedCode
        seq = Sequence()

        mixer_data = self._base_track.devices.mixer_device.to_dict()
        self._base_track.reset_mixer()
        seq.add(self._base_track.save)

        insert_index = self._base_track.sub_tracks[-1].index + 1
        seq.add(partial(self._track_crud_component.create_audio_track, insert_index))
        seq.add(lambda: setattr(Song.selected_track(), "name", self._base_track.name))
        seq.add(lambda: setattr(Song.selected_track(), "color", self._base_track.color))
        seq.add(
            lambda: Song.selected_track().devices.mixer_device.update_from_dict(mixer_data)
        )
        seq.add(lambda: setattr(Song.selected_track().input_routing, "track", self._base_track))
        seq.add(lambda: Song.selected_track().arm_state.arm())
        seq.add(partial(Backend.client().show_success, "Track created, please record clips"))

        return seq.done()
