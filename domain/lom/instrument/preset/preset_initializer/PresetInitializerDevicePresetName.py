from typing import List, Optional

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerInterface import \
    PresetInitializerInterface
from protocol0.domain.shared.utils import find_if
from protocol0.shared.logging.Logger import Logger


class PresetInitializerDevicePresetName(PresetInitializerInterface):
    def get_selected_preset(self, presets):
        # type: (List[InstrumentPreset]) -> Optional[InstrumentPreset]
        assert self._device
        Logger.dev("checking device.preset_name : %s" % self._device.preset_name)
        return find_if(lambda p: p.name == self._device.preset_name, presets)
