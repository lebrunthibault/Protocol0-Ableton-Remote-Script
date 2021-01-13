from typing import List

import Live

from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceChain import DeviceChain


class RackDevice(Device):
    def __init__(self, *a, **k):
        super(RackDevice, self).__init__(*a, **k)
        self._device = self._device  # type: Live.RackDevice.RackDevice
        self.chains = []  # type: (List[DeviceChain])
        self._view = self._device.view  # type: Live.RackDevice.RackDevice.View
        self._chains_listener.subject = self._device
        self._chains_listener()

    @subject_slot("chains")
    def _chains_listener(self):
        self.chains = [DeviceChain(self, chain, index) for index, chain in enumerate(self._device.chains)]

    @property
    def selected_chain(self):
        # type: () -> DeviceChain
        return find_if(lambda c: c._chain == self._view.selected_chain, self.chains)

    def disconnect(self):
        super(RackDevice, self).disconnect()
        [chain.disconnect() for chain in self.chains]
