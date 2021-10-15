from typing import TYPE_CHECKING, List, Any, Type, Optional, Union

import Live
from _Framework.SubjectSlot import subject_slot
from protocol0.enums.DeviceParameterNameEnum import DeviceParameterNameEnum
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.device.DeviceParameter import DeviceParameter
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class Device(AbstractObject):
    def __init__(self, device, track, *a, **k):
        # type: (Live.Device.Device, SimpleTrack, Any, Any) -> None
        super(Device, self).__init__(*a, **k)
        self._device = device
        self.track = track
        self._view = self._device.view  # type: Live.Device.Device.View
        self.parameters = []  # type: (List[DeviceParameter])
        self._parameters_listener.subject = self._device
        self._parameters_listener()
        self.can_have_drum_pads = self._device.can_have_drum_pads
        self.can_have_chains = self._device.can_have_chains

    def __eq__(self, device):
        # type: (object) -> bool
        return isinstance(device, Device) and self._device == device._device

    def update_param_value(self, param_name, param_value):
        # type: (Union[DeviceParameterNameEnum, str], Any) -> None
        param = find_if(lambda p: p.name.lower() == str(param_name).lower(), self.parameters)
        if param and param.is_enabled:
            param.value = param_value

    @staticmethod
    def get_class(device):
        # type: (Any) -> Type[Device]
        if isinstance(device, Live.RackDevice.RackDevice):
            from protocol0.lom.device.RackDevice import RackDevice

            return RackDevice
        elif isinstance(device, Live.PluginDevice.PluginDevice):
            from protocol0.lom.device.PluginDevice import PluginDevice

            return PluginDevice
        elif isinstance(device, Live.SimplerDevice.SimplerDevice):
            from protocol0.lom.device.SimplerDevice import SimplerDevice

            return SimplerDevice
        else:
            return Device

    @staticmethod
    def make(device, track):
        # type: (Live.Device.Device, SimpleTrack) -> Device
        return Device.get_class(device)(device=device, track=track)

    def scroll_presets(self, go_next):
        # type: (bool) -> None
        self.parent.show_message("Presets scrolling is only available for plugin devices")

    @property
    def name(self):
        # type: () -> str
        return self._device.name if self._device else ""

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

    @property
    def mute(self):
        # type: () -> bool
        param = find_if(lambda p: p.original_name.startswith('Device On') and p.is_enabled, self.parameters)
        return param is not None and param.value is True

    @mute.setter
    def mute(self, mute):
        # type: (bool) -> None
        param = find_if(lambda p: p.original_name.startswith('Device On') and p.is_enabled, self.parameters)
        if param:
            param.value = not mute

    @subject_slot("parameters")
    def _parameters_listener(self):
        # type: () -> None
        self.parameters = [DeviceParameter(self, parameter) for parameter in self._device.parameters]

    def disconnect(self):
        # type: () -> None
        super(Device, self).disconnect()
        for parameter in self.parameters:
            parameter.disconnect()
