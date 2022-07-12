from typing import List

from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import (
    PresetImportInterface,
)


class RackDevicePresetImporter(PresetImportInterface):
    def __init__(self, device):
        # type: (RackDevice) -> None
        self._device = device

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        return [
            InstrumentPreset(index=i, name=chain.name)
            for i, chain in enumerate(self._device.chains)
        ]
