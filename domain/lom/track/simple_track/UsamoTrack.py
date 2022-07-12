from typing import Any

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class UsamoTrack(SimpleAudioTrack):
    """
    This track serves 2 purposes

    1. it holds the usamo device that I enabled
    when I'm recording audio (to have sample accurate audio)
    2. it holds a "template dummy clip" that I'm copying
    over when I create dummy tracks
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
