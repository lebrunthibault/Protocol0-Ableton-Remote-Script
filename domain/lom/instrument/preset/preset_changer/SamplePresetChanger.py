from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.SampleSelectedEvent import SampleSelectedEvent
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import PresetChangerInterface
from protocol0.domain.shared.DomainEventBus import DomainEventBus


class SamplePresetChanger(PresetChangerInterface):
    def load(self, preset):
        # type: (InstrumentPreset) -> None
        DomainEventBus.notify(SampleSelectedEvent(str(preset.original_name)))
