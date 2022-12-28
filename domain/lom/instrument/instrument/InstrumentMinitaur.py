from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import \
    PresetProgramSelectedEvent
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerGroupTrackName import (
    PresetInitializerGroupTrackName,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class InstrumentMinitaur(InstrumentInterface):
    NAME = "Minitaur"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = InstrumentColorEnum.MINITAUR
    CAN_BE_SHOWN = False
    PRESETS_PATH = (
        "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    )
    PRESET_OFFSET = 1
    HAS_PROTECTED_MODE = False
    PRESET_INITIALIZER = PresetInitializerGroupTrackName

    def set_default_preset(self):
        # type: () -> None
        DomainEventBus.emit(PresetProgramSelectedEvent(2))
