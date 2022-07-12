from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.preset_changer.InstrumentRackPresetChanger import (
    InstrumentRackPresetChanger,
)


class InstrumentAddictiveKeys(InstrumentInterface):  # noqa
    NAME = "Addictive Keys Piano"
    DEVICE_NAME = "Addictive Keys"
    TRACK_COLOR = InstrumentColorEnum.ADDICTIVE_KEYS
    PRESET_CHANGER = InstrumentRackPresetChanger
