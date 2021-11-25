from typing import Any, List

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.DeviceParameterNameEnum import DeviceParameterNameEnum
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.lom.device.Device import Device
from protocol0.utils.decorators import p0_subject_slot


class DeviceSynchronizer(AbstractControlSurfaceComponent):
    def __init__(self, master, slave, parameter_names, *a, **k):
        # type: (Device, Device, List[DeviceParameterNameEnum], Any, Any) -> None
        super(DeviceSynchronizer, self).__init__(*a, **k)

        self._parameter_synchronizers = []  # type: List[ObjectSynchronizer]

        for parameter_name in parameter_names:
            master_parameter = master.get_parameter_by_name(device_parameter_name=parameter_name)
            slave_parameter = slave.get_parameter_by_name(device_parameter_name=parameter_name)

            if not master_parameter or not slave_parameter:
                self.parent.show_message(
                    "Couldn't find parameter name %s in (%s, %s)" % (parameter_name, master, slave))
                return

            self._parameter_synchronizers.append(ObjectSynchronizer(
                master_parameter, slave_parameter, ["value"]
            ))

        self.abstract_track = master.track.abstract_track
        self.abstract_device = master
        self._abstract_track_has_monitor_in_listener.subject = self.abstract_track

    @p0_subject_slot("has_monitor_in")
    def _abstract_track_has_monitor_in_listener(self):
        # type: () -> None
        self.abstract_device.mute = self.abstract_track.has_monitor_in

    def disconnect(self):
        # type: () -> None
        super(DeviceSynchronizer, self).disconnect()
        for parameter_synchronizer in self._parameter_synchronizers:
            parameter_synchronizer.disconnect()
        self._parameter_synchronizers = []
