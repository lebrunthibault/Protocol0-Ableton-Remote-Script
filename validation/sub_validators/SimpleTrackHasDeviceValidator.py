from typing import Optional

from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.validation.AbstractValidator import AbstractValidator


class SimpleTrackHasDeviceValidator(AbstractValidator):
    def __init__(self, track, device_enum):
        # type: (SimpleTrack, DeviceEnum) -> None
        self._track = track
        self._device_enum = device_enum

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
        return self._track.load_device_from_enum(self._device_enum)
