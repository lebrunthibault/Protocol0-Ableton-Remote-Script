from functools import partial

from typing import Optional

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface


class SimpleTrackHasDeviceValidator(ValidatorInterface):
    def __init__(self, track, device_enum, browser_service):
        # type: (SimpleTrack, DeviceEnum, BrowserServiceInterface) -> None
        self._track = track
        self._device_enum = device_enum
        self._browser_service = browser_service

    def get_error_message(self):
        # type: () -> Optional[str]
        if self.is_valid():
            return None
        return "Couldn't find device %s in %s" % (self._device_enum, self._track)

    def is_valid(self):
        # type: () -> bool
        return self._track.get_device_from_enum(self._device_enum) is not None

    def fix(self):
        # type: () -> Sequence

        seq = Sequence()
        seq.add(self._track.select)
        seq.add(partial(self._browser_service.load_device_from_enum, self._device_enum))
        seq.add(wait=5)
        return seq.done()
