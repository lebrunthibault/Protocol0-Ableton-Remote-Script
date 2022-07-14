from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.SampleSelectedEvent import SampleSelectedEvent
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class SamplePresetChanger(PresetChangerInterface):
    def load(self, preset):
        # type: (InstrumentPreset) -> None
        DomainEventBus.emit(SampleSelectedEvent(str(preset.original_name)))
