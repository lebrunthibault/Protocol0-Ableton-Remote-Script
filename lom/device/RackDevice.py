import Live
from typing import List, Optional, Any

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceChain import DeviceChain
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.utils.utils import find_if


class RackDevice(Device):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(RackDevice, self).__init__(*a, **k)
        self._device = self._device  # type: Live.RackDevice.RackDevice
        self.chains = []  # type: List[DeviceChain]
        self._view = self._device.view  # type: Live.RackDevice.RackDevice.View
        self._chains_listener.subject = self._device
        self._chains_listener()
        self.device_type = DeviceType.RACK_DEVICE
        self.chain_selector = find_if(
            lambda p: p.original_name.startswith("Chain Selector") and p.is_enabled, self.parameters
        )

    @subject_slot("chains")
    def _chains_listener(self):
        # type: () -> None
        self.chains = [DeviceChain(self, chain) for chain in self._device.chains]

    def scroll_chain_selector(self, go_next):
        # type: (bool) -> None
        if not self.chain_selector:
            return
        increment = 1 if go_next else -1
        self.chain_selector.value = (self.chain_selector.value + increment) % len(self.chains)
        self.selected_chain = self.chains[int(self.chain_selector.value)]

    @property
    def selected_chain(self):
        # type: () -> Optional[DeviceChain]
        return find_if(lambda c: c._chain == self._view.selected_chain, self.chains)

    @selected_chain.setter
    def selected_chain(self, selected_chain):
        # type: (DeviceChain) -> None
        self._view.selected_chain = selected_chain._chain

    def disconnect(self):
        # type: () -> None
        super(RackDevice, self).disconnect()
        for chain in self.chains:
            chain.disconnect()
