import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import List


class DeviceChain(SlotManager):
    def __init__(self, chain, index):
        # type: (Live.Chain.Chain, int) -> None
        super(DeviceChain, self).__init__()
        self._chain = chain
        self.index = index
        from protocol0.domain.lom.device.Device import Device

        self.devices = []  # type: List[Device]
        self._devices_listener.subject = self._chain
        self._devices_listener()

    def __repr__(self):
        # type: () -> str
        out = "DeviceChain(name=%s" % self.name
        if len(self.devices):
            out += ", first_device=%s" % self.devices[0]

        return out + ")"

    @property
    def name(self):
        # type: () -> str
        return self._chain.name

    @subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        from protocol0.domain.lom.device.Device import Device

        self.devices = [Device.make(device) for device in self._chain.devices]

    def disconnect(self):
        # type: () -> None
        super(DeviceChain, self).disconnect()
        for device in self.devices:
            device.disconnect()
