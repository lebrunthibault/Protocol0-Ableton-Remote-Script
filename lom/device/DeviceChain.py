import Live
from typing import TYPE_CHECKING, List, Any

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from a_protocol_0.lom.device.Device import Device


class DeviceChain(AbstractObject):
    def __init__(self, device, chain, *a, **k):
        # type: (Device, Live.Chain.Chain, Any, Any) -> None
        super(DeviceChain, self).__init__(*a, **k)
        self.device = device
        self._chain = chain
        self.track = self.device.track
        self.devices = []  # type: List[Device]
        self._devices_listener.subject = self._chain
        self._devices_listener()

    def __repr__(self):
        # type: () -> str
        return self.name

    @property
    def name(self):
        # type: () -> str
        return self._chain.name

    @subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        from a_protocol_0.lom.device.Device import Device

        self.devices = [Device.make(device, self.track) for device in self._chain.devices]

    def disconnect(self):
        # type: () -> None
        super(DeviceChain, self).disconnect()
        for device in self.devices:
            device.disconnect()
