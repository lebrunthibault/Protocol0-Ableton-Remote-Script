from functools import partial
from itertools import chain, imap

from typing import Optional, List, Union
from typing import TYPE_CHECKING

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.track.simple_track.event.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils import find_if

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleTrackActionMixin(object):
    def arm_track(self):
        # type: (SimpleTrack) -> None
        if self.is_armed:
            return None
        if self.is_foldable:
            self.is_folded = not self.is_folded  # type: ignore[has-type]
        else:
            self.mute = False
            self.is_armed = True

        DomainEventBus.notify(SimpleTrackArmedEvent(self))

    def _find_all_devices(self, track_or_chain, only_visible=False):
        # type: (SimpleTrack, Optional[Union[SimpleTrack, DeviceChain]], bool) -> List[Device]
        u""" Returns a list with all devices from a track or chain """
        devices = []
        if track_or_chain is None:
            return []
        for device in filter(None, track_or_chain.devices):  # type: Device
            if not isinstance(device, RackDevice):
                devices += [device]
                continue

            if device.can_have_drum_pads and device.can_have_chains:
                devices += chain([device], self._find_all_devices(device.selected_chain))
            elif not device.can_have_drum_pads and isinstance(device, RackDevice):
                devices += chain(
                    [device],
                    *imap(
                        partial(self._find_all_devices, only_visible=only_visible),
                        filter(None, device.chains),
                    )
                )
        return devices

    def delete_device(self, device_index):
        # type: (SimpleTrack, int) -> None
        self._track.delete_device(device_index)
        self._devices_listener()

    def get_device_from_enum(self, device_enum):
        # type: (SimpleTrack, DeviceEnum) -> Optional[Device]
        return find_if(lambda d: d._name == device_enum.device_name, self.base_track.all_devices)
