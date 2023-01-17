from functools import partial

from typing import Any, cast, Dict, Optional

from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMidiMatchingTrack(AbstractMatchingTrack):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiMatchingTrack, self).__init__(*a, **k)
        from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack

        self._base_track = cast(SimpleMidiTrack, self._base_track)

    def bounce(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        assert all(clip.looping for clip in self._base_track.clips), "Some clips are not looped"
        self._assert_valid_track_name()

        mixer_data = None

        seq = Sequence()
        if self._track is None:
            mixer_data = self._base_track.devices.mixer_device.to_dict()
            self._base_track.reset_mixer()

        seq.add(self._base_track.flatten)
        seq.add(partial(self._post_flatten, mixer_data))
        seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _post_flatten(self, mixer_data):
        # type: (Optional[Dict]) -> None
        flattened_track = Song.selected_track(SimpleAudioTrack)

        if mixer_data is not None:
            flattened_track.devices.mixer_device.update_from_dict(mixer_data)

        if self._track is not None:
            Song.selected_track().output_routing.track = self._track.output_routing.track  # type: ignore[assignment]
