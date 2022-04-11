import collections
from itertools import chain

import Live
from _Framework.SubjectSlot import SlotManager
from typing import List, Optional, Iterator, Dict, cast

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.PluginDeviceAddedEvent import PluginDeviceAddedEvent
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.LiveObjectMapping import LiveObjectMapping
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.utils import find_if
from protocol0.shared.observer.Observable import Observable


class TrackDevices(SlotManager, Observable):
    def __init__(self, live_track):
        # type: (Live.Track.Track) -> None
        super(TrackDevices, self).__init__()
        self._track = live_track
        self._devices = []  # type: List[Device]
        self._all_devices = []  # type: List[Device]
        self._live_device_id_to_device = collections.OrderedDict()  # type: Dict[int, Device]
        self._devices_listener.subject = live_track
        self._devices_mapping = LiveObjectMapping(Device.make)

    def __repr__(self):
        # type: () -> str
        return "TrackDevices(%s, %s)" % (len(self._devices), len(self._all_devices))

    def __iter__(self):
        # type: () -> Iterator[Device]
        return iter(self._devices)

    def build(self):
        # type: () -> None
        self._devices_listener()

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        for device in self._devices:
            device.disconnect()

        self._devices_mapping.build(self._track.devices)
        self._devices = cast(List[Device], self._devices_mapping.all)
        self._all_devices = self._find_all_devices(self._devices)

        if len(self._devices_mapping.added) == 1 and isinstance(self._devices_mapping.added[0], PluginDevice):
            DomainEventBus.notify(PluginDeviceAddedEvent(self._devices_mapping.added[0]))

        self.notify_observers()

    def all(self):
        # type: () -> List[Device]
        return self._all_devices

    @property
    def selected(self):
        # type: () -> Optional[Device]
        if self._track and self._track.view.selected_device:
            device = find_if(
                lambda d: d._device == self._track.view.selected_device, self.all()
            )  # type: Optional[Device]
            assert device
            return device
        else:
            return None

    def get_from_enum(self, device_enum):
        # type: (DeviceEnum) -> Optional[Device]
        return find_if(lambda d: d.name == device_enum.device_name, self._all_devices)

    def _find_all_devices(self, devices, only_visible=False):
        # type: (Optional[List[Device]], bool) -> List[Device]
        u""" Returns a list with all devices from a track or chain """
        all_devices = []
        if devices is None:
            return []
        for device in filter(None, devices):  # type: Device
            if not isinstance(device, RackDevice):
                all_devices += [device]
                continue

            if device.can_have_drum_pads and device.can_have_chains:
                all_devices += chain([device], self._find_all_devices(device.selected_chain.devices))
            elif not device.can_have_drum_pads and isinstance(device, RackDevice):
                all_devices += [device]
                for device_chain in device.chains:
                    all_devices += self._find_all_devices(device_chain.devices, only_visible=only_visible)

        return all_devices

    def delete(self, device):
        # type: (Device) -> None
        if device not in self.all():
            return None

        if device.device_chain:
            device.device_chain.delete_device(device)
        else:
            device_index = self._devices.index(device)
            self._track.delete_device(device_index)
            self.build()
