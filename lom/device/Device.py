from typing import TYPE_CHECKING, List

import Live

from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class Device(AbstractObject):
    def __init__(self, device, track, *a, **k):
        # type: (Live.Device.Device, SimpleTrack) -> None
        super(Device, self).__init__(*a, **k)
        self._device = device
        self.track = track
        self._view = self._device.view
        self.parameters = []  # type: (List[DeviceParameter])
        self._parameters_listener.subject = self._device
        self._parameters_listener()
        self.is_simpler = isinstance(device, Live.SimplerDevice.SimplerDevice)
        self.is_plugin = isinstance(device, Live.PluginDevice.PluginDevice)

    @staticmethod
    def make_device(device, track):
        # type: (Live.Device.Device, SimpleTrack) -> Device
        from a_protocol_0.lom.device.RackDevice import RackDevice
        if isinstance(device, Live.RackDevice.RackDevice):
            return RackDevice(device=device, track=track)
        else:
            return Device(device=device, track=track)

    @property
    def name(self):
        return self._device.name

    @subject_slot("parameters")
    def _parameters_listener(self):
        self.parameters = [DeviceParameter(self, parameter) for parameter in self._device.parameters]

    def get_parameter(self, device_parameter):
        # type: (Live.DeviceParameter.DeviceParameter) -> DeviceParameter
        return find_if(lambda p: p.name == device_parameter.name, self.parameters)

    def disconnect(self):
        super(Device, self).disconnect()
        [parameter.disconnect() for parameter in self.parameters]

