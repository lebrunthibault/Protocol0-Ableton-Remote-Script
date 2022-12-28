import Live
from _Framework.SubjectSlot import SlotManager, subject_slot
from typing import List, Any, Type, Optional, Union

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.shared.utils.list import find_if


class Device(SlotManager):
    def __init__(self, device):
        # type: (Live.Device.Device) -> None
        super(Device, self).__init__()
        self._device = device
        self._view = self._device.view  # type: Live.Device.Device.View
        self.parameters = []  # type: List[DeviceParameter]
        self._parameters_listener.subject = self._device
        self._parameters_listener()
        self.can_have_drum_pads = self._device.can_have_drum_pads  # type: bool
        self.can_have_chains = self._device.can_have_chains  # type: bool


    def __repr__(self):
        # type: () -> str
        return "%s(%s)" % (self.__class__.__name__, self.name)

    @classmethod
    def _get_class(cls, device):
        # type: (Any) -> Type[Device]
        if isinstance(device, Live.RackDevice.RackDevice):
            from protocol0.domain.lom.device.RackDevice import RackDevice
            from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice

            if device.can_have_drum_pads:
                return DrumRackDevice
            else:
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
    def make(cls, device):
        # type: (Live.Device.Device) -> Device
        return Device._get_class(device)(device=device)

    @property
    def enum(self):
        # type: () -> DeviceEnum
        return DeviceEnum.from_value(self.name)

    @subject_slot("parameters")
    def _parameters_listener(self):
        # type: () -> None
        self.parameters = [
            DeviceParameter.create_from_name(self.name, parameter)
            for parameter in self._device.parameters
        ]

    def get_parameter_by_name(self, device_parameter_name):
        # type: (Union[DeviceParameterEnum, str]) -> Optional[DeviceParameter]
        if isinstance(device_parameter_name, DeviceParameterEnum):
            device_parameter_name = device_parameter_name.parameter_name
        return find_if(lambda p: p.name == device_parameter_name, self.parameters)

    @property
    def name(self):
        # type: () -> str
        """Name of the device : user defined"""
        return self._device.name if self._device else ""

    @property
    def class_name(self):
        # type: () -> str
        """type of the device for live devices else PluginDevice"""
        return self._device.class_name if self._device else ""

    @property
    def type_name(self):
        # type: () -> str
        """type of the device (Reverb..) for Live or name of the plugin (FabFilter Pro-Q 3..)"""
        return self.class_name

    @property
    def preset_name(self):
        # type: () -> Optional[str]
        """overridden"""
        return None

    @property
    def is_enabled(self):
        # type: () -> bool
        return self.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON).value == 1

    @is_enabled.setter
    def is_enabled(self, on):
        # type: (bool) -> None
        self.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON).value = 1 if on else 0

    @property
    def is_active(self):
        # type: () -> bool
        """
        Return const access to whether this device is active.
        This will be false both when the device is off and when it's inside a rack device which is off.
        """
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
        self._view.is_collapsed = is_collapsed  # noqa

    @property
    def is_top(self):
        # type: () -> bool
        return isinstance(self._device.canonical_parent, Live.Track.Track)

    def copy_to(self, device):
        # type: (Device) -> None
        for source_param, dest_param in zip(self.parameters, device.parameters):
            dest_param.value = source_param.value
