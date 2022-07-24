from typing import cast

from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.shared.utils.list import find_if


class InstrumentRackPresetChanger(PresetChangerInterface):
    def load(self, preset):
        # type: (InstrumentPreset) -> None
        device = cast(RackDevice, self._device)
        chain_selector = find_if(
            lambda p: p.original_name.startswith("Chain Selector") and p.is_enabled,
            device.parameters,
        )
        chain_selector.value = preset.index
        device.selected_chain = device.chains[preset.index]
