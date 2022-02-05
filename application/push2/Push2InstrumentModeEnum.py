from protocol0.domain.enums.AbstractEnum import AbstractEnum


class Push2InstrumentModeEnum(AbstractEnum):
    SPLIT_MELODIC_SEQUENCER = "split_melodic_sequencer"

    @property
    def label(self):
        # type: () -> str
        return self.value