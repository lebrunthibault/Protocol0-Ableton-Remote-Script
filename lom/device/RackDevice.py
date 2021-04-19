import Live
from typing import List, Optional

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceChain import DeviceChain
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.utils.utils import find_if


class RackDevice(Device):
    def __init__(self, *a, **k):
        super(RackDevice, self).__init__(*a, **k)
        self._device = self._device  # type: Live.RackDevice.RackDevice
        self.chains = []  # type: List[DeviceChain]
        self._view = self._device.view  # type: Live.RackDevice.RackDevice.View
        self._chains_listener.subject = self._device
        self._chains_listener()
        self.device_type = DeviceType.RACK_DEVICE

    @subject_slot("chains")
    def _chains_listener(self):
        self.chains = [DeviceChain(self, chain, index) for index, chain in enumerate(self._device.chains)]

    @property
    def selected_chain(self):
        # type: () -> Optional[DeviceChain]
        return find_if(lambda c: c._chain == self._view.selected_chain, self.chains)

    def disconnect(self):
        super(RackDevice, self).disconnect()
        [chain.disconnect() for chain in self.chains]
