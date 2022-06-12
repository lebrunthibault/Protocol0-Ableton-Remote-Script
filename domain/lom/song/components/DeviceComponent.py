from functools import partial

import Live
from typing import Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.utils.utils import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class DeviceComponent(object):
    def __init__(self, song_view):
        # type: (Live.Song.Song.View) -> None
        self._view = song_view

    @property
    def selected_parameter(self):
        # type: () -> Optional[DeviceParameter]
        all_parameters = [param for track in SongFacade.simple_tracks() for param in track.devices.parameters]
        return find_if(lambda p: p._device_parameter == self._view.selected_parameter, all_parameters)

    def select_device(self, track, device):
        # type: (SimpleTrack, Device) -> Sequence
        seq = Sequence()
        seq.add(track.select)
        seq.add(partial(self._view.select_device, device._device))
        seq.add(ApplicationViewFacade.focus_detail)
        return seq.done()
