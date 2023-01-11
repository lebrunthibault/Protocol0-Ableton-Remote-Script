from functools import partial

from typing import Optional, Any, cast

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.LiveObject import liveobj_valid
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

        seq = Sequence()
        if self._track is None or not liveobj_valid(self._track._track):
            seq.add(partial(track_crud_component.duplicate_track, self._base_track))
            seq.add(self._post_create_matching_track)
            seq.add(self._base_track.save)
            seq.wait_ms(200)
            seq.add(self._base_track.delete)
        else:
            # assert all(
            #     d.enum.should_be_bounced for d in self._base_track.devices
            # ), "Move unbouncable devices"
            seq.add(self._base_track.save)
            seq.add(self._mark_clips_with_automation)
            seq.add(self._base_track.flatten)
            seq.add(self._post_flatten)

        seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _post_create_matching_track(self):
        # type: () -> Sequence
        from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack

        duplicated_track = SongFacade.selected_track(SimpleMidiTrack)
        for device in duplicated_track.devices:
            if not device.enum.should_be_bounced:
                duplicated_track.devices.delete(device)

        seq = Sequence()
        seq.add(duplicated_track.flatten)
        seq.add(self._copy_devices)
        return seq.done()

    def _copy_devices(self):
        # type: () -> None
        devices = [d for d in self._base_track.devices if not d.enum.should_be_bounced]
        Backend.client().show_info("Please copy %s devices: \n%s" % (len(devices), "\n".join(devices)))
        # seq = Sequence()
        #
        # for device in devices:
        #     seq.add(partial(CommandBus.dispatch, LoadDeviceCommand(device.enum.name)))
        #
        # seq.add(partial(self._copy_params, devices))
        #
        # for device in devices:
        #     seq.add(partial(self._base_track.devices.delete, device))
        #
        # return seq.done()

    # def _copy_params(self, devices):
    #     type: # (List[Device]) -> None
        # for index, device in enumerate(devices):
        #     device.copy_to(list(SongFacade.selected_track().devices)[index])

    def _mark_clips_with_automation(self):
        # type: () -> None
        # mark clips with automation
        for clip in self._track.clips:
            has_automation = len(clip.automation.get_automated_parameters(self._track.devices.parameters)) != 0
            if has_automation:
                clip.color = ClipColorEnum.HAS_AUTOMATION.value

    def _post_flatten(self):
        # type: () -> None
        flattened_track = list(SongFacade.simple_tracks())[
            self._base_track.index
        ]  # type: SimpleAudioTrack
        flattened_track.output_routing.track = self._track.output_routing.track  # type: ignore[assignment]
