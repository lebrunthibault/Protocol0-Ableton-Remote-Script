from typing import TYPE_CHECKING, List, Any

import Live
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.lom.device.Device import Device


class DeviceChain(AbstractObject):
    def __init__(self, device, chain, index, *a, **k):
        # type: (Device, Live.Chain.Chain, int, Any, Any) -> None
        super(DeviceChain, self).__init__(*a, **k)
        self.device = device
        self._chain = chain
        self.index = index
        self.track = self.device.track
        self.devices = []  # type: List[Device]
        self._devices_listener.subject = self._chain
        self._devices_listener()

    @property
    def name(self):
        # type: () -> str
        return self._chain.name

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        from protocol0.lom.device.Device import Device

        self.devices = [Device.make(device, self.track, self) for device in self._chain.devices]

    def disconnect(self):
        # type: () -> None
        super(DeviceChain, self).disconnect()
        for device in self.devices:
            device.disconnect()

    def delete_device(self, device):
        # type: (Device) -> None
        device_index = self.devices.index(device)
        self._chain.delete_device(device_index)
        self._devices_listener()
