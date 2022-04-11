from protocol0.domain.lom.device.PluginDevice import PluginDevice


class PluginDeviceAddedEvent(object):
    def __init__(self, device):
        # type: (PluginDevice) -> None
        self.device = device
