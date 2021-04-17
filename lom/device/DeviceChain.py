import Live
from typing import TYPE_CHECKING, List

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from a_protocol_0.lom.device.Device import Device


class DeviceChain(AbstractObject):
    def __init__(self, device, chain, index, *a, **k):
        # type: (Device, Live.Chain.Chain) -> None
        super(DeviceChain, self).__init__(*a, **k)
        self.device = device
        self._chain = chain
        self.index = index
        self.track = self.device.track
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

        self.devices = [Device.make(device, self.track, index) for index, device in enumerate(self._chain.devices)]

    def disconnect(self):
        super(DeviceChain, self).disconnect()
        [device.disconnect() for device in self.devices]
