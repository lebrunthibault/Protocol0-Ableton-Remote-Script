from functools import partial

from typing import Dict, Optional, TYPE_CHECKING

from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class SimpleMatchingTrack(AbstractMatchingTrack):
    def bounce(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        assert all(clip.looping for clip in self._base_track.clips), "Some clips are not looped"
        self._assert_valid_track_name()

        mixer_data = None

        seq = Sequence()
        if self._track is None:
            mixer_data = self._base_track.devices.mixer_device.to_dict()  # type: ignore[has-type]
            self._base_track.reset_mixer()

        seq.add(self._base_track.save)
        seq.add(self._base_track.flatten)
        seq.add(partial(self._post_flatten, mixer_data))
        # if self._base_track.matching_track._track is not None:
        #     seq.add(self._base_track.delete)

        if self._track is None:
            seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _post_flatten(self, mixer_data):
        # type: (Optional[Dict]) -> None
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        flattened_track = Song.selected_track(SimpleAudioTrack)

        if mixer_data is not None:
            flattened_track.devices.mixer_device.update_from_dict(mixer_data)  # type: ignore[has-type]

        if self._track is not None:
            try:
                Song.selected_track().output_routing.track = self._track.output_routing.track  # type: ignore
            except Exception:  # noqa
                pass
