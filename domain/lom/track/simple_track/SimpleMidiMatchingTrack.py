from functools import partial

from typing import Optional, Any, cast, Dict

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMidiMatchingTrack(AbstractMatchingTrack):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiMatchingTrack, self).__init__(*a, **k)
        from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack

        self._base_track = cast(SimpleMidiTrack, self._base_track)

    def connect_base_track(self):
        # type: () -> Optional[Sequence]
        if self._track is None:
            return None

        super(SimpleMidiMatchingTrack, self).connect_base_track()
        seq = Sequence()

        # select the first midi clip
        seq.add(ApplicationViewFacade.show_clip)
        if len(self._base_track.clips) != 0:
            seq.defer()
            seq.add(self._base_track.clips[0].show_notes)

        return seq.done()

    def bounce(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        assert all(clip.looping for clip in self._base_track.clips), "Some clips are not looped"
        self._assert_valid_track_name()

        mixer_data = None

        seq = Sequence()
        if self._track is None:
            mixer_data = self._base_track.devices.mixer_device.to_dict()
            self._base_track.reset_mixer()

        seq.add(self._mark_clips_with_automation)
        seq.add(self._base_track.flatten)
        seq.add(partial(self._post_flatten, mixer_data))
        seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _mark_clips_with_automation(self):
        # type: () -> None
        # mark clips with automation
        if self._track is None:
            return

        for clip in self._track.clips:
            has_automation = (
                len(clip.automation.get_automated_parameters(self._track.devices.parameters)) != 0
            )
            if has_automation:
                clip.color = ClipColorEnum.HAS_AUTOMATION.value

    def _post_flatten(self, mixer_data):
        # type: (Dict) -> None
        flattened_track = list(SongFacade.simple_tracks())[
            self._base_track.index
        ]  # type: SimpleAudioTrack

        if self._track is not None:
            flattened_track.output_routing.track = self._track.output_routing.track  # type: ignore[assignment]
        else:
            flattened_track.devices.mixer_device.update_from_dict(mixer_data)
