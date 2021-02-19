from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.AutomationDeviceType import AutomationDeviceType


class PluginDevice(Device):
    def __init__(self, *a, **k):
        super(PluginDevice, self).__init__(*a, **k)
        self.device_type = AutomationDeviceType.PLUGIN_DEVICE
