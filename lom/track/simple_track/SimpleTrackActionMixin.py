from functools import partial

from typing import Optional
from typing import TYPE_CHECKING

from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.lom.device.Device import Device
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints,PyArgumentList
class SimpleTrackActionMixin(object):
    def arm_track(self):
        # type: (SimpleTrack) -> Optional[Sequence]
        if self.is_armed:
            return None
        if self.is_foldable:
            self.is_folded = not self.is_folded  # type: ignore[has-type]
        else:
            self.mute = False
            self.is_armed = True

        seq = Sequence()
        if self.instrument and self.instrument.needs_exclusive_activation:
            seq.add(partial(self.instrument.activate_plugin_window))
        return seq.done()

    def delete_device(self, device_index):
        # type: (SimpleTrack, int) -> None
        self._track.delete_device(device_index)
        self._devices_listener()

    def get_device_from_enum(self, device_enum):
        # type: (SimpleTrack, DeviceEnum) -> Optional[Device]
        return find_if(lambda d: d.name == device_enum.device_name, self.base_track.all_devices)
