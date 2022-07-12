from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import (
    PresetProgramSelectedEvent,
)
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ProgramChangePresetChanger(PresetChangerInterface):
    def load(self, preset):
        # type: (InstrumentPreset) -> None
        if isinstance(self._device, PluginDevice):
            self._device.selected_preset_index = preset.index
        DomainEventBus.emit(PresetProgramSelectedEvent(preset.index + self._preset_offset))
