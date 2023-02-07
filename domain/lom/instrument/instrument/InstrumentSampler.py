from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentSampler(InstrumentInterface):
    NAME = "Sampler"
    TRACK_COLOR = InstrumentColorEnum.SIMPLER
