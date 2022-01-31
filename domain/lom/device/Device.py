from typing import TYPE_CHECKING, List, Any, Type, Optional, Union

import Live
from protocol0.domain.lom.device.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device.DeviceParameter import DeviceParameter
from protocol0.domain.decorators import p0_subject_slot
from protocol0.domain.utils import find_if

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class Device(AbstractObject):
    def __init__(self, device, track, chain=None, *a, **k):
        # type: (Live.Device.Device, SimpleTrack, Optional[DeviceChain], Any, Any) -> None
        super(Device, self).__init__(*a, **k)
        self._device = device
        self.track = track
        self._view = self._device.view  # type: Live.Device.Device.View
        self.parameters = []  # type: (List[DeviceParameter])
        self._parameters_listener.subject = self._device
        self._parameters_listener()
        self.can_have_drum_pads = self._device.can_have_drum_pads
        self.can_have_chains = self._device.can_have_chains
        self.device_chain = chain

    def __eq__(self, device):
        # type: (object) -> bool
        return isinstance(device, Device) and self._device == device._device

    @staticmethod
    def get_class(device):
        # type: (Any) -> Type[Device]
        if isinstance(device, Live.RackDevice.RackDevice):
            from protocol0.domain.lom.device.RackDevice import RackDevice

            return RackDevice
        elif isinstance(device, Live.PluginDevice.PluginDevice):
            from protocol0.domain.lom.device.PluginDevice import PluginDevice

            return PluginDevice
        elif isinstance(device, Live.SimplerDevice.SimplerDevice):
            from protocol0.domain.lom.device.SimplerDevice import SimplerDevice

            return SimplerDevice
        else:
            return Device

    @staticmethod
    def make(device, track, chain=None):
        # type: (Live.Device.Device, SimpleTrack) -> Device
        return Device.get_class(device)(device=device, track=track, chain=chain)

    def delete(self):
        # type: () -> None
        if self not in self.track.all_devices:
            return None

        if self.device_chain:
            self.device_chain.delete_device(self)
        else:
            device_index = self.track.devices.index(self)
            self.track.delete_device(device_index)

    @property
    def device_on(self):
        # type: () -> bool
        return self.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON).value == 1

    @device_on.setter
    def device_on(self, on):
        # type: (bool) -> None
        self.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON).value = 1 if on else 0
        pass

    def get_parameter_by_name(self, device_parameter_name):
        # type: (Union[DeviceParameterEnum, str]) -> Optional[DeviceParameter]
        if isinstance(device_parameter_name, DeviceParameterEnum):
            device_parameter_name = device_parameter_name.label
        return find_if(lambda d: d.name == device_parameter_name, self.parameters)

    def update_param_value(self, param_name, param_value):
        # type: (Union[DeviceParameterEnum, str], Any) -> None
        param = self.get_parameter_by_name(device_parameter_name=param_name)
        if param and param.is_enabled:
            param.value = param_value

    def scroll_presets(self, go_next):
        # type: (bool) -> None
        raise Protocol0Warning("Presets scrolling is only available for plugin devices")

    @property
    def name(self):
        # type: () -> str
        return self._device.name if self._device else ""

    @property
    def class_name(self):
        # type: () -> str
        return self._device.class_name if self._device else ""

    @property
    def preset_name(self):
        # type: () -> Optional[str]
        """ overridden """
        return None

    @property
    def is_active(self):
        # type: () -> bool
        return self._device.is_active

    @property
    def is_external_device(self):
        # type: () -> bool
        return self.name in ("Ext. Audio Effect", "Ext. Instrument")

    @property
    def is_collapsed(self):
        # type: () -> bool
        return self._view.is_collapsed

    @is_collapsed.setter
    def is_collapsed(self, is_collapsed):
        # type: (bool) -> None
        self._view.is_collapsed = is_collapsed

    @p0_subject_slot("parameters")
    def _parameters_listener(self):
        # type: () -> None
        self.parameters = [DeviceParameter(self, parameter) for parameter in self._device.parameters]

    def disconnect(self):
        # type: () -> None
        super(Device, self).disconnect()
        for parameter in self.parameters:
            parameter.disconnect()
