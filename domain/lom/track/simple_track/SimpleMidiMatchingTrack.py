from functools import partial

from typing import Optional, Any, cast, List

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
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

    def connect_main_track(self):
        # type: () -> Optional[Sequence]
        super(SimpleMidiMatchingTrack, self).connect_main_track()
        seq = Sequence()

        # select the first midi clip
        seq.add(ApplicationViewFacade.show_clip)
        if len(self._base_track.clips) != 0:
            seq.defer()
            seq.add(self._base_track.clips[0].show_notes)

        return seq.done()

    def bounce(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        seq = Sequence()
        if self._track is None or not liveobj_valid(self._track._track):
            seq.add(partial(track_crud_component.duplicate_track, self._base_track))
            seq.add(self._post_create_matching_track)
        else:
            self._copy_params_from_base_track()

        seq.add(self._base_track.focus)
        seq.add(Backend.client().save_track_to_sub_tracks)

        return seq.done()

    def _post_create_matching_track(self):
        # type: () -> Sequence
        from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack

        duplicated_track = SongFacade.selected_track(SimpleMidiTrack)
        for device in duplicated_track.devices:
            if not (device.enum.is_instrument or device.enum.should_be_bounced):
                duplicated_track.devices.delete(device)

        seq = Sequence()
        seq.add(duplicated_track.flatten)
        seq.add(self._copy_devices)
        return seq.done()

    def _copy_devices(self):
        # type: () -> Sequence
        seq = Sequence()

        devices = [d for d in self._base_track.devices if not (d.enum.is_instrument or d.enum.should_be_bounced)]
        for device in devices:
            seq.add(partial(CommandBus.dispatch, LoadDeviceCommand(device.enum.name)))

        seq.add(partial(self._copy_params, devices))

        for device in devices:
            seq.add(partial(self._base_track.devices.delete, device))

        return seq.done()

    def _copy_params(self, devices):
        # type: (List[Device]) -> None
        for index, device in enumerate(devices):
            device.copy_to(list(SongFacade.selected_track().devices)[index])



