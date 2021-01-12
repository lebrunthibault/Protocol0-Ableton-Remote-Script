from typing import TYPE_CHECKING, List

import Live

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.device.Device import Device


class DeviceChain(AbstractObject):
    def __init__(self, device, chain, *a, **k):
        # type: (Device, Live.Chain.Chain) -> None
        super(DeviceChain, self).__init__(*a, **k)
        self.device = device
        self.track = self.device.track
        self._chain = chain
        self.devices = []  # type: List[Device]
        self._devices_listener.subject = self._chain
        self._devices_listener()

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return self._chain.name

    @subject_slot("devices")
    def _devices_listener(self):
        from a_protocol_0.lom.device.Device import Device
        self.devices = [Device.make_device(device, self.track) for device in self._chain.devices]

    def disconnect(self):
        super(DeviceChain, self).disconnect()
        [device.disconnect() for device in self.devices]
