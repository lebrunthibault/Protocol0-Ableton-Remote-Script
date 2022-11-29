from typing import Any

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class UsamoTrack(SimpleMidiTrack):
    """
    This track holds the usamo device that I enabled
    when I'm recording audio (to have sample accurate audio)
    """

    TRACK_NAME = "Usamo"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(UsamoTrack, self).__init__(*a, **k)
        self._usamo_device = self.devices.get_one_from_enum(DeviceEnum.USAMO)
        if self._usamo_device is None:
            raise Protocol0Error("Cannot find usamo device on usamo track")

    def activate(self):
        # type: () -> None
        self._usamo_device.is_enabled = True

    def inactivate(self):
        # type: () -> None
        self._usamo_device.is_enabled = False
