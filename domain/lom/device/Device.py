import Live
from typing import List, Any, Type, Optional, Union

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.utils import find_if


class Device(UseFrameworkEvents):
    def __init__(self, device, chain=None):
        # type: (Live.Device.Device, Optional[DeviceChain]) -> None
        super(Device, self).__init__()
        self._device = device
        self._view = self._device.view  # type: Live.Device.Device.View
        self.parameters = []  # type: List[DeviceParameter]
        self._parameters_listener.subject = self._device
        self._parameters_listener()
        self.can_have_drum_pads = self._device.can_have_drum_pads
        self.can_have_chains = self._device.can_have_chains
        self.device_chain = chain

    def __repr__(self):
        # type: () -> str
        return "%s: %s" % (self.__class__.__name__, self.name)

    @property
    def live_id(self):
        # type: () -> int
        return self._device._live_ptr

    @classmethod
    def _get_class(cls, device):
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

    @classmethod
    def make(cls, device, chain=None):
        # type: (Live.Device.Device, Optional[DeviceChain]) -> Device
        return Device._get_class(device)(device=device, chain=chain)

    @property
    def device_on(self):
        # type: () -> bool
        return self.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON).value == 1

    @device_on.setter
    def device_on(self, on):
        # type: (bool) -> None
        self.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON).value = 1 if on else 0

    def get_parameter_by_name(self, device_parameter_name):
        # type: (Union[DeviceParameterEnum, str]) -> Optional[DeviceParameter]
        if isinstance(device_parameter_name, DeviceParameterEnum):
            device_parameter_name = device_parameter_name.label
        return find_if(lambda p: p.name == device_parameter_name, self.parameters)

    def update_param_value(self, param_name, param_value):
        # type: (Union[DeviceParameterEnum, str], Any) -> None
        param = self.get_parameter_by_name(device_parameter_name=param_name)
        if param and param.is_enabled:
            param.value = param_value

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
        self.parameters = [DeviceParameter(parameter) for parameter in self._device.parameters]
