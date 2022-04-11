import Live
from typing import TYPE_CHECKING, List

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.domain.lom.device.Device import Device


class DeviceChain(UseFrameworkEvents):
    def __init__(self, chain, index):
        # type: (Live.Chain.Chain, int) -> None
        super(DeviceChain, self).__init__()
        self._chain = chain
        self.index = index
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
        from protocol0.domain.lom.device.Device import Device

        self.devices = [Device.make(device, self) for device in self._chain.devices]

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
