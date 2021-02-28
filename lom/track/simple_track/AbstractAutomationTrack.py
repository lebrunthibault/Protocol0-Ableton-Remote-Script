from collections import namedtuple

from typing import Tuple, Optional, Any

from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.device.AutomationDeviceType import AutomationDeviceType
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractAutomationTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AbstractAutomationTrack, self).__init__(*a, **k)
        self._is_hearable = False
        self.nav_view = 'clip'

    @staticmethod
    def get_automation_track_name_from_parameter(parameter):
        # type: (DeviceParameter) -> str
        if parameter.device.device_type == AutomationDeviceType.PLUGIN_DEVICE:
            raise RuntimeError("Plugin devices cannot be automated, use a rack instead: %s" % parameter.device)

        return "%s:%s:%s:%s" % (
            parameter.name, parameter.device.name, parameter.device.device_type, AUTOMATION_TRACK_NAME)

    def get_device_and_parameter(self):
        # type: () -> Tuple[Device, DeviceParameter]
        parameter_info = AbstractAutomationTrack.get_parameter_info(self.base_name)

        return self.parent.deviceManager.get_device_and_parameter_from_name(track=self,
                                                                            device_name=parameter_info.device_name,
                                                                            parameter_name=parameter_info.parameter_name)

    @staticmethod
    def get_parameter_info(track_name):
        # type: (str) -> Optional[Any]
        try:
            [parameter_name, device_name, device_type, _] = track_name.split(":")
        except ValueError:
            return None

        ParameterInfo = namedtuple('ParameterInfo', ['parameter_name', 'device_name', 'device_type'])
        return ParameterInfo(parameter_name, device_name, device_type)
