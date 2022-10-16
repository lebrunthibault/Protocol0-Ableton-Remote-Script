import Live
from _Framework.SubjectSlot import subject_slot
from typing import List, Optional, Any, cast

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.observer.Observable import Observable


class RackDevice(Device, Observable):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(RackDevice, self).__init__(*a, **k)
        self._device = cast(
            Live.RackDevice.RackDevice, self._device
        )  # type: Live.RackDevice.RackDevice
        self.chains = []  # type: List[DeviceChain]
        self._view = self._device.view  # type: Live.RackDevice.RackDevice.View
        self._chains_listener.subject = self._device
        self._chains_listener()

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, DeviceChain):
            self.notify_observers()

    @subject_slot("chains")
    def _chains_listener(self):
        # type: () -> None
        self.chains = [DeviceChain(chain, index) for index, chain in enumerate(self._device.chains)]

        for chain in self.chains:
            chain.register_observer(self)

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
