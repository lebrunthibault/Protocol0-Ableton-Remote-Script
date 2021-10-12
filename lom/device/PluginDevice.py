from typing import List, Any, Optional

import Live
from protocol0.lom.device.Device import Device
from protocol0.utils.utils import scroll_values


class PluginDevice(Device):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(PluginDevice, self).__init__(*a, **k)
        self._device = self._device  # type: Live.PluginDevice.PluginDevice

    def scroll_presets(self, go_next):
        # type: (bool) -> None
        """" unused atm """
        self.parent.navigationManager.focus_detail()
        self.is_collapsed = False
        selected_preset = scroll_values(self.presets, self.selected_preset, go_next)
        self.selected_preset_index = self.presets.index(selected_preset)

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
        """ overridden """
        return self.selected_preset
