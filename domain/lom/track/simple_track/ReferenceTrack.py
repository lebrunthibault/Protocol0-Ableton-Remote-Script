from typing import Any

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.shared.Song import Song


class ReferenceTrack(AbstractGroupTrack):
    TRACK_NAME = "Reference"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ReferenceTrack, self).__init__(*a, **k)
        mastering_rack = Song.master_track().devices.get_one_from_enum(
            DeviceEnum.MASTERING_RACK)
        self._mastering_rack_enabled = mastering_rack is not None and mastering_rack.is_enabled

    def toggle(self):
        # type: () -> None
        mastering_rack = Song.master_track().devices.get_one_from_enum(
            DeviceEnum.MASTERING_RACK)

        if self.muted:
            self.muted = False
            self.solo = True
            if mastering_rack is not None:
                self._mastering_rack_enabled = mastering_rack.is_enabled
                mastering_rack.is_enabled = False
        else:
            self.muted = True
            self.solo = False

            if mastering_rack is not None:
                mastering_rack.is_enabled = self._mastering_rack_enabled
