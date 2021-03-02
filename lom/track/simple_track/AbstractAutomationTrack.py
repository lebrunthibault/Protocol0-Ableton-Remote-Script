from collections import namedtuple

from typing import Tuple, Optional, Any

from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.device.DeviceType import DeviceType
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
        from a_protocol_0 import Protocol0
        if parameter is None:
            raise Protocol0Error("You passed None to get_automation_track_name_from_parameter, selected_track : %s" % Protocol0.SELF.protocol0_song.selected_track)

        if parameter.device.device_type == DeviceType.PLUGIN_DEVICE:
            raise Protocol0Error("Plugin devices cannot be automated, use a rack instead: %s" % parameter.device)

        return "%s:%s:%s:%s" % (
            parameter.name, parameter.device.name, parameter.device.device_type, AUTOMATION_TRACK_NAME)

    @staticmethod
    def get_parameter_info_from_track_name(track_name):
        # type: (str) -> Optional[Any]
        try:
            [parameter_name, device_name, device_type, _] = track_name.split(":")
        except ValueError:
            return None

        ParameterInfo = namedtuple('ParameterInfo', ['parameter_name', 'device_name', 'device_type'])
        return ParameterInfo(parameter_name, device_name, device_type)
