from typing import List

import Live

from _Framework.SubjectSlot import subject_slot

class RackDevice(Device):
    def __init__(self, *a, **k):
        super(RackDevice, self).__init__(*a, **k)
        self.chains = []  # type: (List[DeviceChain])
        self._chains_listener.subject = self._device
        self._chains_listener()

    @subject_slot("chains")
    def _chains_listener(self):
        self.chains = [DeviceChain(self, chain) for chain in self._device.chains]

