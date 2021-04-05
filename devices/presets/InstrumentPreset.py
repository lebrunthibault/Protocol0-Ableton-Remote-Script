import os

from typing import TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentPreset(AbstractObject):
    def __init__(self, instrument, index, name="empty", *a, **k):
        # type: (AbstractInstrument, int, str) -> None
        super(InstrumentPreset, self).__init__(*a, **k)
        self.instrument = instrument
        self.index = index
        self.original_name = name
        self.name = self._format_name(name)

    def __repr__(self):
        return "%s (%s)" % (self.name, self.index + 1)

    def _format_name(self, name):
        if not name:
            return None

        base_preset_name = os.path.splitext(name)[0]  # remove file extension
        return self.instrument.format_preset_name(base_preset_name)  # calling subclass formatting
