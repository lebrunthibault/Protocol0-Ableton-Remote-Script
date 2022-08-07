import Live
from typing import List, Any, Optional, cast

from protocol0.domain.lom.device.Device import Device


class PluginDevice(Device):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(PluginDevice, self).__init__(*a, **k)
        self._device = cast(
            Live.PluginDevice.PluginDevice, self._device
        )  # type: Live.PluginDevice.PluginDevice

    @property
    def presets(self):
        # type: () -> List[str]
        return [str(preset) for preset in list(self._device.presets) if not str(preset) == "empty"]

    @property
    def selected_preset_index(self):
        # type: () -> int
        return self._device.selected_preset_index

    @selected_preset_index.setter
    def selected_preset_index(self, selected_preset_index):
        # type: (int) -> None
        self._device.selected_preset_index = selected_preset_index

    @property
    def selected_preset(self):
        # type: () -> str
        return self.presets[self.selected_preset_index]

    @property
    def preset_name(self):
        # type: () -> Optional[str]
        """overridden"""
        return self.selected_preset

    @property
    def type_name(self):
        # type: () -> str
        return self.name
